import argparse
import csv
import re

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
CATEGORIES = [
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the description text.
    Returns: dict with applied keys: category, priority, reason, flag added.
    """
    description = row.get('description', '').lower()
    
    # 1. Determine Category
    category = 'Other'
    flag = 'NEEDS_REVIEW'
    
    if 'pothole' in description:
        category = 'Pothole'
        flag = ''
    elif 'flood' in description or 'water' in description:
        category = 'Flooding'
        flag = ''
    elif 'streetlight' in description or 'lights out' in description:
        category = 'Streetlight'
        flag = ''
    elif 'waste' in description or 'garbage' in description or 'animal' in description:
        category = 'Waste'
        flag = ''
    elif 'music' in description or 'noise' in description:
        category = 'Noise'
        flag = ''
    elif 'road surface' in description or 'footpath' in description or 'manhole' in description or 'crack' in description:
        category = 'Road Damage'
        flag = ''
    elif 'drain' in description:
        category = 'Drain Blockage'
        flag = ''
    elif 'heritage' in description and 'damage' in description:
        category = 'Heritage Damage'
        flag = ''
        
    # 2. Determine Priority
    priority = 'Standard'
    matched_severity_keyword = None
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = 'Urgent'
            matched_severity_keyword = kw
            break
            
    # 3. Formulate Reason
    if matched_severity_keyword:
        reason = f"The description contains the critical keyword '{matched_severity_keyword}'."
    else:
        # Just grab the first few meaningful words
        words = description.split()[:5]
        snippet = " ".join(words)
        reason = f"The issue was categorized based on the phrase '{snippet}' in the description."
        
    # Copy row and add new fields
    result = dict(row)
    result['category'] = category
    result['priority'] = priority
    result['reason'] = reason
    result['flag'] = flag
    
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row safely, and write the augmented results to the output CSV.
    """
    processed_rows = []
    fieldnames = []
    
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames)
        
        # Ensure new columns exist
        for col in ['category', 'priority', 'reason', 'flag']:
            if col not in fieldnames:
                fieldnames.append(col)
                
        for row in reader:
            try:
                if not row or all(not v for v in row.values()):
                    # Flag null rows
                    row['flag'] = 'NULL_ROW'
                    processed_rows.append(row)
                    continue
                    
                processed_row = classify_complaint(row)
                processed_rows.append(processed_row)
            except Exception as e:
                # Do not crash on bad rows
                row['flag'] = f"ERROR: {str(e)}"
                processed_rows.append(row)
                
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
