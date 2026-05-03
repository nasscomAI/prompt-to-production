"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to agent and skills definitions.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '')
    complaint_id = row.get('complaint_id', '')
    categories = ['Pothole', 'Flooding', 'Garbage', 'Streetlight']
    urgent_keywords = ['injury', 'accident', 'hospital', 'school', 'child']
    reason = []
    category = 'Other'
    flag = ''
    desc_lower = description.lower()

    # Category detection
    for cat in categories:
        if cat.lower() in desc_lower:
            category = cat
            reason.append(cat)
            break
    else:
        # Try keyword-based mapping
        if 'road' in desc_lower or 'hole' in desc_lower:
            category = 'Pothole'
            reason.append('road/hole')
        elif 'water' in desc_lower or 'flood' in desc_lower:
            category = 'Flooding'
            reason.append('water/flood')
        elif 'garbage' in desc_lower or 'trash' in desc_lower or 'waste' in desc_lower:
            category = 'Garbage'
            reason.append('garbage/trash/waste')
        elif 'light' in desc_lower or 'lamp' in desc_lower:
            category = 'Streetlight'
            reason.append('light/lamp')
        else:
            category = 'Other'
            flag = 'NEEDS_REVIEW'
            reason.append('ambiguous')

    # Priority detection
    priority = 'Normal'
    for word in urgent_keywords:
        if word in desc_lower:
            priority = 'Urgent'
            reason.append(word)
            break

    # Reason field
    reason_str = ', '.join(reason)

    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason_str,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    results = []
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                if not row.get('description'):
                    result = {
                        'complaint_id': row.get('complaint_id', ''),
                        'category': 'Other',
                        'priority': 'Normal',
                        'reason': 'No description',
                        'flag': 'NEEDS_REVIEW'
                    }
                else:
                    result = classify_complaint(row)
            except Exception as e:
                result = {
                    'complaint_id': row.get('complaint_id', ''),
                    'category': 'Other',
                    'priority': 'Normal',
                    'reason': f'Error: {e}',
                    'flag': 'ERROR'
                }
            results.append(result)

    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
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
