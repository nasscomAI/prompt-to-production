"""
UC-0A — Complaint Classifier
Built based on agents.md and skills.md.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = str(row.get("description", "")).lower()
    complaint_id = row.get("complaint_id", row.get("id", ""))
    
    # 1. Determine Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_urgent_kw = None
    
    for kw in urgent_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', description):
            priority = "Urgent"
            found_urgent_kw = kw
            break
            
    # 2. Determine Category
    kw_map = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlog", "water log", "submerged", "flooding"],
        "Streetlight": ["streetlight", "street light", "dark street", "lamp"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "dump"],
        "Noise": ["noise", "loud music", "party", "loud"],
        "Road Damage": ["road damage", "crack", "broken road"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat hazard", "extreme heat"],
        "Drain Blockage": ["drain block", "clogged drain", "drain", "sewage"]
    }
    
    matches = []
    for cat, kws in kw_map.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', description):
                matches.append((cat, kw))
                
    unique_categories = set([m[0] for m in matches])
    category = "Other"
    flag = ""
    found_category_kw = None
    
    if len(unique_categories) == 1:
        category = list(unique_categories)[0]
        found_category_kw = [m[1] for m in matches if m[0] == category][0]
    elif len(unique_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(unique_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 3. Formulate Reason (Exactly one sentence citing specific words)
    reasons = []
    if found_category_kw:
        reasons.append(f"categorized based on the word '{found_category_kw}'")
    if found_urgent_kw:
        reasons.append(f"marked Urgent due to the word '{found_urgent_kw}'")
        
    if reasons:
        reason = "The complaint was " + " and ".join(reasons) + "."
    else:
        reason = "No recognizable keywords were found in the description."
        
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
    Flags nulls, doesn't crash on bad rows, produces output even if some rows fail.
    """
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8', newline='') as f_out:
        
        reader = csv.DictReader(f_in)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            try:
                # Basic validation for completely null rows
                if not row or not any(row.values()):
                    writer.writerow({
                        "complaint_id": "UNKNOWN",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "The row was completely empty.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue

                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                print(f"Error processing row: {e}")
                writer.writerow({
                    "complaint_id": row.get("complaint_id", row.get("id", "UNKNOWN")),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing failed with error: {str(e)}.",
                    "flag": "NEEDS_REVIEW"
                })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
