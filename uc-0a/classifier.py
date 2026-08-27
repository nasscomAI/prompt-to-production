"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md and skills.md.
    Returns: dict with updated keys: category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Severity keywords triggering 'Urgent' priority
    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    
    # Determine Priority
    priority = "Standard"
    found_severity = None
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            found_severity = kw
            break

    # Taxonomy Mapping
    categories_map = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "lights out", "dark", "sparking"],
        "Waste": ["waste", "garbage", "trash", "animal", "dumped"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["road damage", "crack", "broken", "sinking"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "sun"],
        "Drain Blockage": ["drain", "manhole", "block"]
    }

    # Determine Category
    category = "Other"
    reason_word = ""
    match_found = False
    
    for cat, keywords in categories_map.items():
        if match_found:
            break
        for kw in keywords:
            if kw in description:
                category = cat
                reason_word = kw
                match_found = True
                break

    # Determine Refusal / Ambiguity flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Create one-sentence Reason citing description strings
    if flag == "NEEDS_REVIEW":
        reason = "The complaint was ambiguous lacking exact keywords, defaulting to Other."
    else:
        if found_severity:
            reason = f"The description quotes '{reason_word}' for category and '{found_severity}' triggering highest priority."
        else:
            reason = f"The description specifically quotes '{reason_word}' allowing normal matching."

    row['category'] = category
    row['priority'] = priority
    row['reason'] = reason
    row['flag'] = flag
    
    return row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            if not rows:
                print("Input CSV is empty.")
                return
            
            fieldnames = []
            _fn = reader.fieldnames
            if _fn is not None:
                fieldnames.extend(_fn)
                
            for field in ['category', 'priority', 'reason', 'flag']:
                if field not in fieldnames:
                    fieldnames.append(field)
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in rows:
                try:
                    classified_row = classify_complaint(row)
                    writer.writerow(classified_row)
                except Exception as row_error:
                    row['category'] = "Other"
                    row['priority'] = "Low"
                    row['reason'] = f"Processing error: {str(row_error)}."
                    row['flag'] = "NEEDS_REVIEW"
                    writer.writerow(row)
                    
    except Exception as e:
        print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
