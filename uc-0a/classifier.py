"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

# Enforcement Rule Mappings
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding"],
    "Streetlight": ["streetlight", "darkness", "street light"],
    "Waste": ["waste", "garbage", "trash"],
    "Noise": ["noise", "drilling", "loud"],
    "Road Damage": ["crater", "collapsed"],
    "Heritage Damage": ["heritage damage", "monument damage"],
    "Heat Hazard": ["heat", "temperature"],
    "Drain Blockage": ["drain blocked", "drain completely blocked", "drain 100% blocked"]
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority Enforcement
    priority = "Standard"
    severity_triggers = []
    for word in SEVERITY_KEYWORDS:
        if word in desc:
            priority = "Urgent"
            severity_triggers.append(word)
            
    # Category Enforcement
    matched = []
    category_triggers = []
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in desc:
                matched.append(cat)
                category_triggers.append(kw)
                break
                
    # Ambiguity Enforcement
    flag = ""
    assigned_category = "Other"
    
    if len(matched) == 1:
        assigned_category = matched[0]
    elif len(matched) > 1:
        assigned_category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        assigned_category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Formatting Reason Statement
    all_triggers = list(set(severity_triggers + category_triggers))
    if not all_triggers:
        all_triggers = ["general issue"]
        
    reason = f"Classified due to the presence of terms like '{all_triggers[0]}' in the description."

    return {
        "complaint_id": row.get("complaint_id", "unknown"),
        "category": assigned_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f_in, open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            reader = csv.DictReader(f_in)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                # Handle nulls/bad rows gracefully
                if not row or not row.get("complaint_id"):
                    continue
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception as e:
                    writer.writerow({
                        "complaint_id": row.get("complaint_id", "unknown"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System Error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Could not find '{input_path}'")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
