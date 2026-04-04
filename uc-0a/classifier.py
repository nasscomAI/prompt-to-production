"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlog"],
    "Streetlight": ["streetlight", "street light", "lamp", "dark"],
    "Waste": ["waste", "garbage", "trash", "dump"],
    "Noise": ["noise", "loud", "sound"],
    "Road Damage": ["road", "broken road", "surface"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "sun", "temperature"],
    "Drain Blockage": ["drain", "block", "clog"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority check
    found_severe = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    priority = "Urgent" if found_severe else "Standard"
    
    # Category check
    matched_categories = []
    matched_kws = []
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in desc:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                matched_kws.append(kw)
    
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = "Other" 
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    reason_kws = list(set(found_severe + matched_kws))
    if reason_kws:
        reason = f"Classified based on keywords: {', '.join(reason_kws)}."
    else:
        reason = "No matching keywords found in description."
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    fieldnames = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if 'category' not in fieldnames: fieldnames.append('category')
            if 'priority' not in fieldnames: fieldnames.append('priority')
            if 'reason' not in fieldnames: fieldnames.append('reason')
            if 'flag' not in fieldnames: fieldnames.append('flag')
                
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    row.update(classified)
                    results.append(row)
                except Exception as e:
                    row['flag'] = 'ERROR'
                    results.append(row)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
