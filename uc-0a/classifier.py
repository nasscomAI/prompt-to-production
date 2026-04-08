import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row deterministically based on RICE enforcement rules.
    """
    desc = row.get('description', '').lower()
    
    # Priority schema
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_sev = [kw for kw in severity_keywords if kw in desc]
    priority = 'Urgent' if found_sev else 'Standard'
    
    # Category schema mapping
    cat_keywords = {
        'Pothole': ['pothole', 'crater'],
        'Drain Blockage': ['drain', 'block'],
        'Flooding': ['flood', 'rainwater'],
        'Noise': ['noise', 'drilling', 'engine', 'loud'],
        'Waste': ['waste', 'garbage', 'trash', 'debris'],
        'Road Damage': ['collapse', 'road damage', 'crack'],
        'Heritage Damage': ['heritage', 'monument', 'historic'],
        'Streetlight': ['streetlight', 'light', 'dark'],
        'Heat Hazard': ['heat', 'temperature', 'sun']
    }
    
    matched_cats = []
    found_cat_kw = []
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in desc:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                found_cat_kw.append(kw)
    
    # Ambiguity check
    if len(matched_cats) == 1:
        category = matched_cats[0]
        flag = ''
        
        # Resolve reason
        pri_kw = found_sev[0] if found_sev else 'no severity keywords'
        cat_kw = found_cat_kw[0]
        if priority == 'Urgent':
            reason = f"Categorized as {category} and Urgent because the text mentions '{cat_kw}' and '{pri_kw}'."
        else:
            reason = f"Categorized as {category} with Standard priority because it mentions '{cat_kw}'."
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        if len(matched_cats) > 1:
            reason = f"Ambiguous complaint matching multiple categories: {', '.join(matched_cats)}."
        else:
            reason = "Category could not be determined definitively from description."
            
    # Include original complaint_id if exists
    result = {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Error: Input CSV has no headers.")
                return
            
            # The output will include all original fields plus our 4 new fields
            out_fieldnames = fieldnames + ['category', 'priority', 'reason', 'flag']
            
            rows_to_write = []
            for row in reader:
                # Handle effectively null rows by checking if 'description' exists and has len > 0
                if not row.get('description') or not str(row['description']).strip():
                    row['category'] = 'Other'
                    row['priority'] = 'Low'
                    row['reason'] = 'No description provided.'
                    row['flag'] = 'NEEDS_REVIEW'
                    rows_to_write.append(row)
                    continue
                    
                classification = classify_complaint(row)
                row['category'] = classification['category']
                row['priority'] = classification['priority']
                row['reason'] = classification['reason']
                row['flag'] = classification['flag']
                rows_to_write.append(row)
                
        with open(output_path, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
    except Exception as e:
        print(f"Error processing files: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
