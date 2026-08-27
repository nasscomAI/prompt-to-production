"""
UC-0A — Complaint Classifier
Built according to RICE -> agents.md -> skills.md constraints.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = {
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
}

URGENT_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

CATEGORY_KEYWORDS = {
    'Pothole': ['pothole'],
    'Flooding': ['flood', 'flooding', 'flooded'],
    'Streetlight': ['streetlight', 'lights', 'dark', 'sparking'],
    'Waste': ['garbage', 'waste', 'dumped', 'animal'],
    'Noise': ['music', 'noise', 'weeknights'],
    'Road Damage': ['cracked', 'sinking', 'broken', 'upturned'],
    'Heritage Damage': ['heritage'],
    'Heat Hazard': ['heat'],
    'Drain Blockage': ['drain', 'manhole'],
}

def classify_complaint(row: dict) -> dict:
    description = str(row.get('description', '')).lower()
    
    category = None
    priority = 'Standard'
    reason_words = []
    flag = ''
    
    # 1. Determine Category
    matched_categories = []
    for cat_name, keywords in CATEGORY_KEYWORDS.items():
        matched = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', description)]
        if matched:
            matched_categories.append(cat_name)
            reason_words.extend(matched)
            
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        
    # 2. Assign Priority
    urgent_matches = [kw for kw in URGENT_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', description)]
    if urgent_matches:
        priority = 'Urgent'
        reason_words.extend(urgent_matches)
        
    # 3. Formulate Reason
    if reason_words:
        unique_reason_words = list(dict.fromkeys(reason_words))
        reason = f"Mentioned: {', '.join(unique_reason_words)}."
    else:
        reason = "Could not identify distinct classification triggers."

    if category not in ALLOWED_CATEGORIES:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        
    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
    results = []
    for row in rows:
        try:
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            results.append({
                'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                'category': 'Other',
                'priority': 'Standard',
                'reason': f'Error processing: {str(e)}',
                'flag': 'NEEDS_REVIEW'
            })
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
