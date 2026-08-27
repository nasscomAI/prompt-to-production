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
    desc = str(row.get('description', '')).lower()
    
    # Priority rules
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_severity = [kw for kw in severity_keywords if kw in desc]
    priority = "Urgent" if matched_severity else "Standard"
    
    # Category rules
    cat_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "rain"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["garbage", "waste", "dump", "animal", "smell"],
        "Noise": ["music", "noise"],
        "Road Damage": ["road", "crack", "sink", "footpath", "tile"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain"]
    }
    
    matched_categories = []
    matched_cat_kws = []
    for cat, kws in cat_keywords.items():
        matched = [kw for kw in kws if kw in desc]
        if matched:
            matched_categories.append(cat)
            matched_cat_kws.extend(matched)
            
    # Ambiguity check & assignment
    if len(matched_categories) == 1:
        category = matched_categories[0]
        reason = f"Classified as {category} based on keywords: {', '.join(matched_cat_kws)}."
        flag = ""
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous categories detected ({', '.join(matched_categories)}) based on keywords: {', '.join(matched_cat_kws)}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not confidently determine category from description."
        
    if matched_severity:
        reason += f" Priority set to Urgent due to severity keywords: {', '.join(matched_severity)}."

    result = row.copy()
    result['category'] = category
    result['priority'] = priority
    result['reason'] = reason
    result['flag'] = flag
    
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    fieldnames = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Make sure we don't duplicate keys if they already exist in the input CSV somehow
            existing_fields = list(reader.fieldnames)
            new_fields = ['category', 'priority', 'reason', 'flag']
            fieldnames = existing_fields + [f for f in new_fields if f not in existing_fields]
            
            for row in reader:
                try:
                    # check for nulls
                    if not row.get('description') or row.get('description').strip() == '':
                        row['category'] = "Other"
                        row['priority'] = "Standard"
                        row['reason'] = "Description is null or empty."
                        row['flag'] = "NEEDS_REVIEW"
                        results.append(row)
                        continue
                        
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id', 'Unknown')}: {e}")
                    err_row = row.copy()
                    err_row['category'] = "Other"
                    err_row['priority'] = "Standard"
                    err_row['reason'] = f"Classification failed: {str(e)}"
                    err_row['flag'] = "NEEDS_REVIEW"
                    results.append(err_row)
    except Exception as e:
        print(f"Error reading input file {input_path}: {e}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

