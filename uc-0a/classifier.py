"""
UC-0A — Complaint Classifier
Classifies citizen complaint records into categories and priorities
based on agents.md enforcement rules and skills.md specifications.
"""
import argparse
import csv
import re
from typing import Dict, List, Optional

# Allowed categories — exact strings only, no variations
VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category keyword mappings
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "hole in road", "road hole", "pit in road"],
    "Flooding": ["flood", "flooding", "flooded", "waterlogging", "water logged", "submerged", "inundated"],
    "Streetlight": ["streetlight", "street light", "lamp post", "light not working", "no light", "dark street"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "litter", "dump", "dumping", "refuse"],
    "Noise": ["noise", "loud", "noisy", "sound", "honking", "blaring", "cacophony"],
    "Road Damage": ["road damage", "damaged road", "road crack", "crack in road", "road broken", "asphalt", "tarmac"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "heritage site", "heritage building"],
    "Heat Hazard": ["heat", "hot", "heatwave", "sunstroke", "heat stroke", "extreme heat", "temperature"],
    "Drain Blockage": ["drain", "drainage", "blocked drain", "clogged drain", "sewer", "sewage", "overflow drain"]
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row into category, priority, reason, and flag.
    
    Args:
        row: dict with keys: id, description
    
    Returns:
        dict with keys: id, category, priority, reason, flag
    """
    complaint_id = row.get("id", "")
    description = row.get("description", "")
    
    # Handle empty or unreadable descriptions
    if not description or not description.strip():
        return {
            "id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Unable to classify — empty description",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # Determine category
    category = _determine_category(description_lower)
    
    # Determine priority
    priority = _determine_priority(description_lower)
    
    # Generate reason citing specific words
    reason = _generate_reason(description, category)
    
    # Determine flag
    flag = "" if category != "Other" else "NEEDS_REVIEW"
    
    return {
        "id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _determine_category(description_lower: str) -> str:
    """
    Determine the category based on keyword matching in description.
    Returns the first matching category or 'Other' if no match found.
    """
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    return "Other"


def _determine_priority(description_lower: str) -> str:
    """
    Determine priority based on presence of urgency keywords.
    Returns 'Urgent' if any severity keyword is found, otherwise 'Standard'.
    """
    for keyword in URGENT_KEYWORDS:
        if keyword in description_lower:
            return "Urgent"
    return "Standard"


def _generate_reason(description: str, category: str) -> str:
    """
    Generate a reason sentence citing specific words from the description.
    """
    description_lower = description.lower()
    
    # Find the matching keywords in the description for the determined category
    matched_words = []
    if category in CATEGORY_KEYWORDS:
        for keyword in CATEGORY_KEYWORDS[category]:
            if keyword in description_lower:
                # Find the actual word in original description
                idx = description_lower.find(keyword)
                actual_word = description[idx:idx + len(keyword)]
                matched_words.append(actual_word)
    
    # Find urgency keywords if present
    urgency_words = []
    for keyword in URGENT_KEYWORDS:
        if keyword in description_lower:
            idx = description_lower.find(keyword)
            actual_word = description[idx:idx + len(keyword)]
            urgency_words.append(actual_word)
    
    # Build reason
    if matched_words:
        words_str = ", ".join(matched_words[:3])  # Limit to first 3 matches
        reason = f"Description mentions '{words_str}' indicating a {category.lower()} issue"
    else:
        reason = f"Complaint text suggests a {category.lower()} related problem"
    
    if urgency_words:
        urgency_str = ", ".join(urgency_words[:2])
        reason += f" with urgency due to '{urgency_str}'"
    
    return reason


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Args:
        input_path: Path to input CSV with 'id' and 'description' columns
        output_path: Path to write output CSV
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Validate input has required columns
            if not reader.fieldnames or 'description' not in reader.fieldnames:
                raise ValueError(f"Input CSV must contain 'id' (or 'complaint_id') and 'description' columns. Found: {reader.fieldnames}")
            
            # Determine the ID column name
            id_col = 'id' if 'id' in reader.fieldnames else 'complaint_id' if 'complaint_id' in reader.fieldnames else None
            if not id_col:
                raise ValueError(f"Input CSV must contain 'id' or 'complaint_id' column. Found: {reader.fieldnames}")
            
            results = []
            failures = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Normalize row to use 'id' key
                    normalized_row = {"id": row.get(id_col, ""), "description": row.get("description", "")}
                    result = classify_complaint(normalized_row)
                    results.append(result)
                except Exception as e:
                    failures.append({"row": row_num, "error": str(e)})
                    # Add a fallback result with NEEDS_REVIEW flag
                    results.append({
                        "id": row.get(id_col, ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification failed: {str(e)[:100]}",
                        "flag": "NEEDS_REVIEW"
                    })
            
            # Write output CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                fieldnames = ["id", "category", "priority", "reason", "flag"]
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            # Log failures if any
            if failures:
                print(f"Warning: {len(failures)} rows failed classification:")
                for f in failures:
                    print(f"  Row {f['row']}: {f['error']}")
            
            print(f"Processed {len(results)} complaints. Results written to {output_path}")
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except csv.Error as e:
        raise ValueError(f"Malformed CSV file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
