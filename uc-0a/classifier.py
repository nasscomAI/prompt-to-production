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
    description = row.get("description", "").lower()
    
    # Check Priority Rules (Urgent if severity keywords present)
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    found_urgent_kw = None
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            found_urgent_kw = kw
            break
            
    # Check Category Rules
    category_map = {
        'pothole': 'Pothole',
        'flood': 'Flooding',
        'rain': 'Flooding',
        'streetlight': 'Streetlight',
        'light': 'Streetlight',
        'dark': 'Streetlight',
        'waste': 'Waste',
        'garbage': 'Waste',
        'animal': 'Waste',
        'dump': 'Waste',
        'noise': 'Noise',
        'music': 'Noise',
        'crack': 'Road Damage',
        'sink': 'Road Damage',
        'footpath': 'Road Damage',
        'heritage': 'Heritage Damage',
        'heat': 'Heat Hazard',
        'drain': 'Drain Blockage',
        'manhole': 'Drain Blockage',
    }
    
    found_cats = set()
    found_cat_kws = []
    for kw, cat in category_map.items():
        if kw in description:
            found_cats.add(cat)
            found_cat_kws.append(kw)
            
    flag = ""
    category = "Other"
    reason_parts = []
    
    if len(found_cats) == 1:
        category = list(found_cats)[0]
        reason_parts.append(f"description mentions '{found_cat_kws[0]}'")
    elif len(found_cats) > 1:
        category = list(found_cats)[0]
        flag = "NEEDS_REVIEW"
        reason_parts.append(f"ambiguous category (found {', '.join(found_cat_kws)})")
    else:
        flag = "NEEDS_REVIEW"
        reason_parts.append("could not definitively determine category")
        
    if priority == "Urgent":
        reason_parts.append(f"priority is Urgent due to severity keyword '{found_urgent_kw}'")
        
    reason = "Classified based on: " + " and ".join(reason_parts) + "."
    
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # We assume input has 'complaint_id', 'description', etc.
        fieldnames = list(reader.fieldnames)
        for new_field in ['category', 'priority', 'reason', 'flag']:
            if new_field not in fieldnames:
                fieldnames.append(new_field)
        rows = list(reader)
        
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            try:
                classification = classify_complaint(row)
                row.update(classification)
            except Exception as e:
                row.update({
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error parsing row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
