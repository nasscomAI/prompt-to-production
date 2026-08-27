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
    description = row.get('description', '')
    complaint_id = row.get('complaint_id', '')

    if not description:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'Description is missing.',
            'flag': 'NEEDS_REVIEW'
        }

    desc_lower = description.lower()

    # Priorities
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = 'Standard'
    urgent_word_found = None
    for word in urgent_keywords:
        if word in desc_lower:
            priority = 'Urgent'
            urgent_word_found = word
            break

    # Categories
    category_map = {
        'Pothole': ['pothole'],
        'Flooding': ['flood'],
        'Streetlight': ['streetlight', 'light', 'dark'],
        'Waste': ['garbage', 'waste', 'dump', 'dead animal'],
        'Noise': ['music', 'noise', 'loud'],
        'Road Damage': ['crack', 'road surface', 'footpath', 'road'],
        'Heritage Damage': ['heritage', 'monument'],
        'Heat Hazard': ['heat hazard'],
        'Drain Blockage': ['drain', 'manhole']
    }

    assigned_category = 'Other'
    cat_word_found = None
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in desc_lower:
                assigned_category = cat
                cat_word_found = kw
                break
        if assigned_category != 'Other':
            break

    # Flag
    flag = 'NEEDS_REVIEW' if assigned_category == 'Other' else ''

    # Reason
    reason = ""
    if assigned_category == 'Other':
        reason = "Classified as Other because the description does not strongly match any specific category."
    else:
        reason = f"Classified as {assigned_category} because it mentions '{cat_word_found}'."
        
    if priority == 'Urgent':
        reason += f" Priority is Urgent due to the severity keyword '{urgent_word_found}'."

    return {
        'complaint_id': complaint_id,
        'category': assigned_category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, 'r', encoding='utf-8') as f_in, open(output_path, 'w', encoding='utf-8', newline='') as f_out:
        reader = csv.DictReader(f_in)
        
        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
