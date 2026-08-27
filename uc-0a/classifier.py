"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")
    
    # Check severity for priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if kw in desc]
    priority = "Urgent" if found_urgent else "Standard"
    
    if found_urgent:
        reason = f"The description mentions '{found_urgent[0]}'."
    else:
        reason = "The description mentions no severe danger."
        
    # Categories
    mapping = {
        "pothole": "Pothole", "flooding": "Flooding", "streetlight": "Streetlight",
        "waste": "Waste", "noise": "Noise", "road damage": "Road Damage",
        "heritage damage": "Heritage Damage", "heat hazard": "Heat Hazard",
        "drain blockage": "Drain Blockage"
    }
    
    found_categories = [v for k, v in mapping.items() if k in desc]
    
    flag = ""
    if len(found_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Category is genuinely ambiguous or could not be determined."
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Multiple overlapping categories detected; ambiguous."
    else:
        category = found_categories[0]
        
    # Overwrite reason if there's no urgent found but we matched a category
    if not found_urgent and category != "Other":
        reason = f"The description mentions the '{category.lower()}' issue."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return
        
    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for row in rows:
            try:
                desc_val = row.get("description")
                if desc_val is None or str(desc_val).strip() == "":
                    writer.writerow({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Empty or null description",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                
                res = classify_complaint(row)
                writer.writerow(res)
            except Exception as e:
                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error processing: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
