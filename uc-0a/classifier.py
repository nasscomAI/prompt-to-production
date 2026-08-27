import csv

# Severity keywords that trigger Urgent
SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

# Allowed categories
CATEGORIES = [
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise',
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
]

def classify_complaint(row: dict) -> dict:
    desc = row['description'].lower()
    
    # Default
    category = 'Other'
    priority = 'Standard'
    flag = ''
    reason = ''

    # Category detection (simple keyword matching)
    if 'pothole' in desc:
        category = 'Pothole'
    elif 'flood' in desc or 'underpass' in desc:
        category = 'Flooding'
    elif 'streetlight' in desc or 'light out' in desc:
        category = 'Streetlight'
    elif 'garbage' in desc or 'waste' in desc or 'bin' in desc:
        category = 'Waste'
    elif 'noise' in desc or 'music' in desc or 'loud' in desc:
        category = 'Noise'
    elif 'road' in desc or 'crack' in desc or 'manhole' in desc or 'footpath' in desc:
        category = 'Road Damage'
    elif 'heritage' in desc:
        category = 'Heritage Damage'
    elif 'heat' in desc:
        category = 'Heat Hazard'
    elif 'drain' in desc or 'blocked' in desc:
        category = 'Drain Blockage'

    # Urgent priority if severity keywords appear
    if any(k in desc for k in SEVERITY_KEYWORDS):
        priority = 'Urgent'

    # Reason
    reason = f"Based on description: {row['description'][:100]}"

    # If still Other, flag for review
    if category == 'Other':
        flag = 'NEEDS_REVIEW'

    return {
        'complaint_id': row['complaint_id'],
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = [classify_complaint(row) for row in rows]

    # Write output
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['complaint_id','category','priority','reason','flag'])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")