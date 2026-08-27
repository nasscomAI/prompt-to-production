"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# Allowed categories from schema
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
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", 
    "fell", "collapse"
}

# Category keywords for classification
CATEGORY_KEYWORDS = {
    "Pothole": {
        "primary": ["pothole", "hole", "pit"],
        "modifiers": ["tyre", "tire", "vehicle", "affected"],
    },
    "Flooding": {
        "primary": ["flood", "flooded", "knee-deep", "water"],
        "modifiers": ["stranded", "commuters", "inaccessible"],
    },
    "Streetlight": {
        "primary": ["streetlight", "light", "lighting"],
        "modifiers": ["out", "dark", "flickering", "sparking", "electrical"],
    },
    "Waste": {
        "primary": ["garbage", "waste", "trash", "bins", "dumped", "dead animal"],
        "modifiers": ["overflowing", "smell", "health", "renovation"],
    },
    "Noise": {
        "primary": ["noise", "music", "sound"],
        "modifiers": ["midnight", "loud", "nuisance"],
    },
    "Road Damage": {
        "primary": ["road", "surface", "cracked", "sinking", "crack", "manhole", "footpath", "tiles", "broken", "upturned"],
        "modifiers": ["damage", "utility", "cyclists", "missing", "injury", "elderly"],
    },
    "Heritage Damage": {
        "primary": ["heritage", "old city", "historic"],
        "modifiers": ["lights", "safety", "street"],
    },
    "Heat Hazard": {
        "primary": ["heat", "hazard", "temperature"],
        "modifiers": ["extreme", "hot", "temperature"],
    },
    "Drain Blockage": {
        "primary": ["drain", "blockage", "blocked", "clogged"],
        "modifiers": ["water", "flooded"],
    },
}


def contains_severity_keyword(description: str) -> bool:
    """Check if description contains any severity keyword."""
    description_lower = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description_lower:
            return True
    return False


def extract_category_reason(description: str) -> tuple:
    """
    Classify complaint into category and extract reasoning.
    Returns: (category, reason, is_ambiguous)
    """
    description_lower = description.lower()
    
    # Score each category based on keyword matches
    category_scores = {}
    category_reasons = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        primary_matches = [kw for kw in keywords["primary"] if kw in description_lower]
        modifier_matches = [kw for kw in keywords["modifiers"] if kw in description_lower]
        
        score = len(primary_matches) * 2 + len(modifier_matches)
        category_scores[category] = score
        category_reasons[category] = primary_matches + modifier_matches
    
    # Find top categories
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    
    if sorted_categories[0][1] == 0:
        # No keywords matched
        return "Other", "No matching keywords found in description.", True
    
    top_category_score = sorted_categories[0][1]
    top_categories = [cat for cat, score in sorted_categories if score == top_category_score]
    
    is_ambiguous = len(top_categories) > 1 or top_category_score < 2
    
    chosen_category = top_categories[0]
    matched_words = category_reasons[chosen_category]
    
    # Build reason from matched keywords
    if matched_words:
        matched_words_str = ", ".join(f'"{w}"' for w in matched_words[:3])
        reason = f"Description mentions {matched_words_str}, indicating {chosen_category}."
    else:
        reason = f"Classification based on complaint content suggests {chosen_category}."
    
    return chosen_category, reason, is_ambiguous


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    Enforces RICE rules from agents.md.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    
    # Handle missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    # Extract category and reason
    category, reason, is_ambiguous = extract_category_reason(description)
    
    # Determine priority based on severity keywords
    has_severity = contains_severity_keyword(description)
    if has_severity:
        priority = "Urgent"
    else:
        # Default to Standard; could be Low if clear low-severity keywords
        priority = "Standard"
    
    # Set flag if ambiguous
    flag = "NEEDS_REVIEW" if is_ambiguous else ""
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Enforces error handling: continues on bad rows, produces output regardless.
    """
    results = []
    
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            
            if not reader.fieldnames:
                print(f"Error: Input file {input_path} has no headers.")
                return
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (row 1 is headers)
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    print(f"Warning: Error processing row {row_num}: {str(e)}")
                    complaint_id = row.get("complaint_id", f"ROW_{row_num}") if row else f"ROW_{row_num}"
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Row processing failed.",
                        "flag": "NEEDS_REVIEW"
                    })
    
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        return
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return
    
    # Write results to output CSV
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Classified {len(results)} complaints successfully.")
    
    except Exception as e:
        print(f"Error writing output file: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
