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
    Implements RICE enforcement rules from agents.md and skills.md.
    """
    description = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', '')
    categories = {
        'pothole': ['pothole', 'road', 'hole'],
        'flooding': ['flood', 'waterlogging', 'rain'],
        'garbage': ['garbage', 'trash', 'waste'],
        'streetlight': ['streetlight', 'light', 'lamp'],
        'water': ['water', 'pipe', 'supply'],
    }
    priority_keywords = ['injury', 'child', 'school', 'hospital']
    reason_keywords = []
    category = 'Other'
    flag = ''
    # Category detection
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in description:
                category = cat.capitalize()
                reason_keywords.append(kw)
                break
        if category != 'Other':
            break
    # Priority detection
    priority = 'Normal'
    for kw in priority_keywords:
        if kw in description:
            priority = 'Urgent'
            reason_keywords.append(kw)
    # Reason extraction
    reason = ', '.join(set(reason_keywords)) if reason_keywords else 'No specific keywords found.'
    # Enforcement: If category cannot be determined, flag for review
    if category == 'Other':
        flag = 'NEEDS_REVIEW'
    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
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
                # Flag nulls
                if not row.get('description'):
                    result = {
                        'complaint_id': row.get('complaint_id', ''),
                        'category': 'Other',
                        'priority': 'Normal',
                        'reason': 'No description provided.',
                        'flag': 'NEEDS_REVIEW'
                    }
                else:
                    result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    'complaint_id': row.get('complaint_id', ''),
                    'category': 'Other',
                    'priority': 'Normal',
                    'reason': f'Error: {str(e)}',
                    'flag': 'NEEDS_REVIEW'
                })
    # Write results
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
