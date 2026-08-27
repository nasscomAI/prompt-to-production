"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules in agents.md.
    Returns: dict with appended keys: category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Default values for ambiguous descriptions
    category = "Other"
    priority = "Standard"
    reason = "Could not confidently identify explicit classification terms."
    flag = "NEEDS_REVIEW"
    
    if not description:
        row.update({"category": category, "priority": priority, "reason": "Empty description.", "flag": flag})
        return row

    # 1. Enforcement rule: Priority mapped to Urgent if keywords present
    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    
    found_severities = [kw for kw in severity_keywords if kw in description]
    if found_severities:
        priority = "Urgent"
        priority_reason = f"contains severity keyword '{found_severities[0]}'"
    else:
        priority_reason = "no severity keywords present"

    # 2. Enforcement rule: Exact match mapping for Category
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "lights out", "dark at night", "sparking"],
        "Waste": ["garbage", "waste", "dead animal", "smell"],
        "Noise": ["music", "noise"],
        "Road Damage": ["road surface cracked", "manhole cover missing", "tiles broken", "crack", "surface"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain"]
    }
    
    found_category = None
    matched_word = ""
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in description:
                found_category = cat
                matched_word = kw
                break
        if found_category:
            break
            
    # 3. Enforcement: one sentence reason sighting words & 4. Needs Review flag
    if found_category:
        category = found_category
        flag = ""
        reason = f"Categorized as {category} sighting '{matched_word}' in description, assigned {priority} because {priority_reason}."
    else:
        reason = f"Category ambiguous due to missing exact match words; assigned {priority} because {priority_reason}."
        flag = "NEEDS_REVIEW"

    row["category"] = category
    row["priority"] = priority
    row["reason"] = reason
    row["flag"] = flag
    return row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = list(csv.DictReader(infile))
            
            if not reader:
                print("Input CSV is empty.")
                return

            fieldnames = list(reader[0].keys())
            new_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
            new_fieldnames = list(dict.fromkeys(new_fieldnames))
            
            processed_rows = []
            for row in reader:
                try:
                    processed_row = classify_complaint(row.copy())
                    processed_rows.append(processed_row)
                except Exception as e:
                    print(f"Failed processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    row["category"] = "Other"
                    row["priority"] = "Standard"
                    row["reason"] = "Row processing failed due to error."
                    row["flag"] = "NEEDS_REVIEW"
                    processed_rows.append(row)
                    
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)
            
    except Exception as e:
        print(f"Error accessing files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
