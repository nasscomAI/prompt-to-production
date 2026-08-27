import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on R.I.C.E enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = str(row.get('description', '')).lower()
    
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    categories_map = {
        'Pothole': ['pothole', 'crater'],
        'Drain Blockage': ['drain', 'manhole', 'sewage', 'blocked'],
        'Flooding': ['flood', 'water'],
        'Streetlight': ['streetlight', 'light', 'dark'],
        'Waste': ['garbage', 'waste', 'trash', 'animal', 'dumped', 'bin'],
        'Noise': ['noise', 'music', 'loud'],
        'Road Damage': ['road surface', 'crack', 'sinking', 'footpath', 'tiles'],
        'Heritage Damage': ['heritage', 'monument'],
        'Heat Hazard': ['heat', 'temperature']
    }
    
    # Evaluate Priority
    priority = "Standard"
    urgent_trigger = None
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            urgent_trigger = kw
            break
            
    # Evaluate Category
    category = "Other"
    cat_trigger = None
    flag = ""
    
    for cat, kws in categories_map.items():
        for kw in kws:
            if kw in description:
                category = cat
                cat_trigger = kw
                break
        if cat_trigger:
            break
            
    # Enforce formatting rules
    if category == "Other":
        flag = "NEEDS_REVIEW"
        priority = "Low"
        reason = "The category could not be explicitly determined from the description alone, flagging for review."
    else:
        if priority == "Urgent":
            reason = f"Classified as {category} citing '{cat_trigger}', and escalated to Urgent due to '{urgent_trigger}'."
        else:
            reason = f"Classified as {category} based explicitly on the keyword '{cat_trigger}' found in the description."
            
    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, and ensure output is consistently generated.
    """
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Enforce handling of null or corrupt rows
                    if not row.get('description') or row.get('description').strip() == "":
                        raise ValueError("Missing description")
                        
                    classification = classify_complaint(row)
                    
                    # Merge classification with original fields
                    out_row = dict(row)
                    out_row.update(classification)
                    results.append(out_row)
                    
                except Exception as e:
                    out_row = dict(row)
                    out_row.update({
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f"Classification failed ({str(e)}).",
                        'flag': 'NEEDS_REVIEW'
                    })
                    results.append(out_row)
                    
    except Exception as e:
        print(f"Error reading input CSV file: {e}")
        return
        
    if not results:
        print("No valid rows processed. Output file will not be written.")
        return
        
    try:
        # Use fieldnames from the first processed row, adding any new columns
        fieldnames = list(results[0].keys())
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output CSV file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Classified records successfully written to {args.output}")
