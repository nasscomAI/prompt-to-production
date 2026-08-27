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
    
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    cat_keywords = {
        'Pothole': ['pothole', 'crater'],
        'Flooding': ['flood', 'water', 'underpass'],
        'Streetlight': ['streetlight', 'light', 'dark'],
        'Waste': ['waste', 'garbage', 'trash', 'animal'],
        'Noise': ['noise', 'loud', 'music'],
        'Road Damage': ['road', 'crack', 'sink', 'manhole', 'footpath', 'tile'],
        'Heritage Damage': ['heritage', 'monument'],
        'Heat Hazard': ['heat'],
        'Drain Blockage': ['drain', 'block', 'clog']
    }
    
    found_sev = [kw for kw in severity_keywords if kw in desc]
    priority = "Urgent" if found_sev else "Standard"
    
    matched_cats = []
    reason_word = None
    
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in desc:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                if not reason_word:
                    reason_word = kw
                    
    flag = ""
    if len(matched_cats) > 1:
        flag = "NEEDS_REVIEW"
        category = matched_cats[0]
    elif len(matched_cats) == 1:
        category = matched_cats[0]
    else:
        category = "Other"
        
    cited_word = found_sev[0] if found_sev else (reason_word if reason_word else "complaint")
    reason = f"The description mentions '{cited_word}'."
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            fieldnames = reader.fieldnames
            if not fieldnames:
                return
                
            out_fields = fieldnames + ["category", "priority", "reason", "flag"]
            out_fields = list(dict.fromkeys(out_fields))
            rows = list(reader)
            
        with open(output_path, 'w', encoding='utf-8', newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=out_fields)
            writer.writeheader()
            
            for row in rows:
                try:
                    res = classify_complaint(row)
                    row.update(res)
                    writer.writerow(row)
                except Exception as e:
                    print(f"Error processing row: {e}")
                    
    except Exception as e:
        print(f"Failed to process batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
