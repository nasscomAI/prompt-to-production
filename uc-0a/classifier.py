"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority
    priority = "Standard"
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_severity = [kw for kw in severity_keywords if kw in desc]
    if found_severity:
        priority = "Urgent"
        
    # Category matches
    cat_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "rain"],
        "Streetlight": ["streetlight", "light", "spark"],
        "Waste": ["garbage", "waste", "dump", "smell", "animal"],
        "Noise": ["music", "noise"],
        "Road Damage": ["crack", "sinking", "manhole", "broken", "footpath", "road surface"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain"]
    }
    
    matched_cats = set()
    found_cat_words = []
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in desc:
                matched_cats.add(cat)
                found_cat_words.append(kw)
                
    category = "Other"
    flag = ""
    reason = ""
    
    # Special case: heritage + light = ambiguous or streetlight? 
    # Let's let the heuristic flag it if multiple match
    
    if len(matched_cats) == 1:
        category = list(matched_cats)[0]
        reason_words = list(set(found_cat_words + found_severity))
        reason = f"Classified based on citing words from description: {', '.join(reason_words)}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Genuinely ambiguous or lacking clear single category."
        
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
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            try:
                res = classify_complaint(row)
                row['category'] = res['category']
                row['priority'] = res['priority']
                row['reason'] = res['reason']
                row['flag'] = res['flag']
                results.append(row)
            except Exception as e:
                row['category'] = "Other"
                row['priority'] = "Standard"
                row['reason'] = "Error reading complaint description."
                row['flag'] = "NEEDS_REVIEW"
                results.append(row)
                
    out_fields = list(fieldnames)
    for col in ['category', 'priority', 'reason', 'flag']:
        if col not in out_fields:
            out_fields.append(col)
            
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
