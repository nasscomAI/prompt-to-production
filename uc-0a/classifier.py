import argparse
import csv

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

CATEGORIES = {
    'Pothole': ['pothole'],
    'Flooding': ['flood', 'flooding', 'floods'],
    'Streetlight': ['streetlight', 'lights out', 'dark', 'lights'],
    'Waste': ['garbage', 'waste', 'dead animal', 'dumped', 'smell', 'bin'],
    'Noise': ['music', 'noise', 'loud'],
    'Road Damage': ['cracked', 'sinking', 'tiles broken', 'manhole', 'road surface', 'footpath'],
    'Heritage Damage': ['heritage'],
    'Heat Hazard': ['heat'],
    'Drain Blockage': ['drain'],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get('description', '')).lower()
    
    # Priority
    priority = 'Standard'
    for k in SEVERITY_KEYWORDS:
        if k in desc:
            priority = 'Urgent'
            break
            
    # Category Identification
    matched_cats = {}
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in desc:
                if cat not in matched_cats:
                    matched_cats[cat] = []
                matched_cats[cat].append(kw)
    
    category = 'Other'
    flag = ''
    reason = 'No specific keywords found matching defined categories.'
    
    if len(matched_cats) == 0:
        flag = 'NEEDS_REVIEW'
        reason = 'No distinct category identified from the description.'
    elif len(matched_cats) == 1:
        category = list(matched_cats.keys())[0]
        words = matched_cats[category]
        reason = f"Classified based on presence of the word '{words[0]}' in description."
    else:
        # Multiple categories found
        category = list(matched_cats.keys())[0]
        flag = 'NEEDS_REVIEW'
        all_words = []
        for v in matched_cats.values():
            all_words.extend(v)
        reason = f"Ambiguous complaint mentioning multiple flags: {', '.join(all_words)}."

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
    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                results.append({
                    'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                    'category': 'Other',
                    'priority': 'Low',
                    'reason': f'Error processing row: {e}',
                    'flag': 'NEEDS_REVIEW'
                })

    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['complaint_id', 'category', 'priority', 'reason', 'flag'])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
