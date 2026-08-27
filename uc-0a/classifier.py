"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

CATEGORIES = {
    'Pothole': ['pothole', 'tyre damage'],
    'Flooding': ['flood', 'water'],
    'Streetlight': ['streetlight', 'lights out', 'sparking', 'dark'],
    'Waste': ['garbage', 'waste', 'dead animal', 'dumped'],
    'Noise': ['music', 'noise', 'loud'],
    'Road Damage': ['road surface', 'crack', 'sinking', 'footpath tiles'],
    'Heritage Damage': ['heritage'],
    'Heat Hazard': ['heat'],
    'Drain Blockage': ['drain', 'manhole']
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    matched_categories = []
    category_reasons = []
    
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in desc:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    category_reasons.append(kw)
    
    # Needs review if ambiguous
    flag = ''
    if len(matched_categories) == 0:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        cat_reason = 'no matching keywords'
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        flag = 'NEEDS_REVIEW'
        cat_reason = f"multiple keywords ({', '.join(category_reasons)})"
    else:
        category = matched_categories[0]
        cat_reason = category_reasons[0]
        
    # Priority
    priority = 'Standard'
    priority_reason = ''
    matched_severity = []
    for skw in SEVERITY_KEYWORDS:
        if skw in desc:
            matched_severity.append(skw)
    
    if matched_severity:
        priority = 'Urgent'
        priority_reason = matched_severity[0]
        
    reason_words = [cat_reason]
    if priority_reason:
        reason_words.append(priority_reason)
    
    if flag == 'NEEDS_REVIEW' and category == 'Other':
        reason = "Category is ambiguous because no known keywords were found."
    else:
        reason = f"Classified as {category} with {priority} priority because the description mentions '{' and '.join(reason_words)}'."
    
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
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            # We want to keep original fields except date_raised etc, or we can just append/output specific ones.
            # The prompt says: "uc-0a/results_[your-city].csv"
            # It should have complaint_id, category, priority, reason, flag
            
            out_fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            
            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
                writer.writeheader()
                
                for row_idx, row in enumerate(reader, start=1):
                    try:
                        result = classify_complaint(row)
                        writer.writerow(result)
                    except Exception as e:
                        # Fallback for malformed rows
                        print(f"Error processing row {row_idx}: {e}")
                        writer.writerow({
                            'complaint_id': row.get('complaint_id', f'unknown_{row_idx}'),
                            'category': 'Other',
                            'priority': 'Low',
                            'reason': f"Error during classification: {e}",
                            'flag': 'NEEDS_REVIEW'
                        })
    except FileNotFoundError:
        print(f"Error: Could not find input file: {input_path}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
