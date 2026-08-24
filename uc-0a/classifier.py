"""
UC-0A — Complaint Classifier
Implements RICE enforcement rules from agents.md and skills.md.
"""
import argparse
import csv
import re
from typing import Dict, Tuple

# Allowed categories (closed set)
ALLOWED_CATEGORIES = {
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
}

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {
    "injury", "injured", "child", "children", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse", "risk", "serious"
}

# Category keyword patterns (prioritized by specificity)
CATEGORY_PATTERNS = {
    "Pothole": ["pothole", "crater", "pit", "rut", "sinkhole", "cavity"],
    "Flooding": ["flood", "flooded", "water", "inundated", "submerged", "waterlogged", "stranded", "knee-deep"],
    "Streetlight": ["streetlight", "streetlights", "light", "lights", "lamp", "sparking", "flickering", "electrical hazard"],
    "Waste": ["garbage", "waste", "trash", "debris", "dump", "dumped", "litter", "bins", "overflowing"],
    "Noise": ["noise", "sound", "music", "loud", "disturb", "midnight"],
    "Road Damage": ["crack", "cracked", "sinking", "surface", "damaged road", "asphalt", "tiles", "upturned"],
    "Heritage Damage": ["heritage", "historic", "monument", "old city", "ancient"],
    "Heat Hazard": ["heat", "temperature", "sun", "burning", "thermal"],
    "Drain Blockage": ["drain", "blockage", "clogged", "sewer", "underground", "manhole"]
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to agents.md/skills.md rules.
    
    Input: dict with keys: complaint_id, description, location (at minimum)
    Output: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces:
    1. Category must be exact match from allowed list
    2. Priority is Urgent if ANY severity keyword present
    3. Reason must cite 2+ specific words from description
    4. Flag = NEEDS_REVIEW if ambiguous
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    
    # Initialize output
    result = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": "",
        "flag": ""
    }
    
    # Handle empty description
    if not description:
        result["reason"] = "No description provided."
        result["flag"] = "NEEDS_REVIEW"
        return result
    
    desc_lower = description.lower()
    
    # RULE 1: Check for severity keywords → Urgent priority
    has_severity = False
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', desc_lower):
            result["priority"] = "Urgent"
            has_severity = True
            break
    
    # RULE 2: Match category from keyword patterns
    matched_categories = []
    match_counts = {}  # Track how many keywords match per category
    
    for category, patterns in CATEGORY_PATTERNS.items():
        count = 0
        for pattern in patterns:
            if re.search(r'\b' + re.escape(pattern) + r'\b', desc_lower):
                count += 1
        if count > 0:
            matched_categories.append(category)
            match_counts[category] = count
    
    # Resolve category with confidence-based ambiguity detection
    if len(matched_categories) == 1:
        # Single match: confident classification
        result["category"] = matched_categories[0]
    elif len(matched_categories) > 1:
        # Multiple matches: check if one dominates
        max_count = max(match_counts.values())
        dominant_categories = [cat for cat in matched_categories if match_counts[cat] == max_count]
        
        if len(dominant_categories) == 1:
            # One category has more matches: use it
            result["category"] = dominant_categories[0]
        else:
            # Multiple categories tied or equal: ambiguous. Use Other and flag.
            result["category"] = "Other"
            result["flag"] = "NEEDS_REVIEW"
    else:
        # No clear match: use Other and flag for review
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
    
    # RULE 3: Generate reason citing specific words from description
    reason = _generate_reason(description, result["category"])
    result["reason"] = reason if reason else "Complaint details insufficient for detailed reasoning."
    
    # ENFORCEMENT: Verify all output fields are valid
    assert result["priority"] in ["Urgent", "Standard", "Low"], f"Invalid priority: {result['priority']}"
    assert result["category"] in ALLOWED_CATEGORIES, f"Invalid category: {result['category']}"
    assert result["flag"] in ["NEEDS_REVIEW", ""], f"Invalid flag: {result['flag']}"
    assert len(result["reason"]) > 0, "Reason field cannot be empty"
    
    return result


def _generate_reason(description: str, category: str) -> str:
    """
    Extract 2+ concrete words from description that justify the category.
    Returns one sentence with specific details from the description.
    """
    # Extract key nouns and adjectives from description
    words = description.split()
    
    # Heuristic: look for words > 4 chars or domain-specific terms
    relevant_words = []
    keywords_by_category = {
        "Pothole": ["pothole", "crater", "pit", "rut", "sinkhole", "tyre", "damage", "vehicles"],
        "Flooding": ["flood", "flooded", "water", "waterlogged", "stranded", "inundated", "submerged", "knee-deep"],
        "Streetlight": ["streetlight", "streetlights", "light", "lights", "flickering", "sparking", "electrical", "dark"],
        "Waste": ["garbage", "waste", "trash", "bins", "dumped", "overflowing", "debris"],
        "Noise": ["noise", "music", "midnight", "loud", "disturb", "weeknights"],
        "Road Damage": ["crack", "cracked", "sinking", "surface", "asphalt", "tiles", "upturned", "broken"],
        "Heritage Damage": ["heritage", "historic", "monument", "lights", "pedestrians"],
        "Heat Hazard": ["heat", "temperature", "thermal", "burning"],
        "Drain Blockage": ["drain", "blockage", "clogged", "manhole", "sewer"],
        "Other": []
    }
    
    # Collect words that appear in category keywords for this category
    for word in words:
        word_lower = word.lower().rstrip('.,;:!?')
        if len(word_lower) > 3:  # Skip short words
            if category in keywords_by_category:
                for kw in keywords_by_category[category]:
                    if kw in word_lower or word_lower in kw:
                        relevant_words.append(word_lower)
                        break
    
    # Remove duplicates while preserving order
    seen = set()
    unique_words = []
    for w in relevant_words:
        if w not in seen:
            unique_words.append(w)
            seen.add(w)
    
    if unique_words:
        # Use first 3 relevant words for reason
        cited_words = ", ".join(unique_words[:3])
        return f"Specific details: {cited_words}."
    else:
        # Fallback: extract first few non-trivial words from description
        extracted = []
        for word in words[:15]:
            cleaned = word.lower().rstrip('.,;:!?')
            if len(cleaned) > 3 and cleaned not in ["that", "this", "near", "area", "road", "street", "location"]:
                extracted.append(cleaned)
                if len(extracted) >= 3:
                    break
        if extracted:
            return f"Reported: {', '.join(extracted)}."
    
    return "Complaint details provided."


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Implements error handling: skip bad rows, log errors, produce output 
    even if some rows fail.
    """
    results = []
    error_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            if reader.fieldnames is None:
                print(f"ERROR: {input_path} has no header row.")
                return
            
            row_num = 0
            for row in reader:
                row_num += 1
                try:
                    # Validate required fields
                    if not row.get("complaint_id"):
                        print(f"WARNING: Row {row_num} missing complaint_id, skipping.")
                        error_count += 1
                        continue
                    
                    if not row.get("description"):
                        print(f"WARNING: Row {row_num} (ID: {row['complaint_id']}) missing description, skipping.")
                        error_count += 1
                        continue
                    
                    # Classify this row
                    classified = classify_complaint(row)
                    results.append(classified)
                    
                except Exception as e:
                    print(f"ERROR processing row {row_num}: {e}")
                    error_count += 1
                    continue
        
        # Write output CSV
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Processed {row_num} rows. Classified {len(results)} successfully. {error_count} errors.")
        
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}")
    except Exception as e:
        print(f"FATAL ERROR: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
