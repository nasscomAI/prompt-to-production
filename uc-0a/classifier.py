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
    desc = row.get('description', '').strip()
    complaint_id = row.get('complaint_id', '')

    if not desc:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'Description is missing.',
            'flag': 'NEEDS_REVIEW'
        }

    desc_lower = desc.lower()

    # 1. Category mapping
    category = "Other"
    category_reasons = []
    
    if 'pothole' in desc_lower or 'crater' in desc_lower:
        category = 'Pothole'
        category_reasons.append('pothole/crater')
    elif 'flood' in desc_lower or 'waterlogged' in desc_lower:
        category = 'Flooding'
        category_reasons.append('flood/waterlogged')
    elif 'streetlight' in desc_lower or 'lights out' in desc_lower or 'dark' in desc_lower:
        if 'heritage' in desc_lower:
            category = 'Heritage Damage'
            category_reasons.append('heritage')
        else:
            category = 'Streetlight'
            category_reasons.append('streetlight/dark')
    elif 'garbage' in desc_lower or 'waste' in desc_lower or 'animal' in desc_lower or 'smell' in desc_lower:
        category = 'Waste'
        category_reasons.append('waste/smell')
    elif 'music' in desc_lower or 'noise' in desc_lower or 'loud' in desc_lower:
        category = 'Noise'
        category_reasons.append('noise/music')
    elif 'road surface' in desc_lower or 'crack' in desc_lower or 'footpath' in desc_lower:
        category = 'Road Damage'
        category_reasons.append('road damage')
    elif 'heritage' in desc_lower or 'monument' in desc_lower:
        category = 'Heritage Damage'
        category_reasons.append('heritage')
    elif 'heat' in desc_lower or 'sun' in desc_lower:
        category = 'Heat Hazard'
        category_reasons.append('heat')
    elif 'drain' in desc_lower or 'sewer' in desc_lower or 'manhole' in desc_lower:
        category = 'Drain Blockage'
        category_reasons.append('drain/manhole')

    flag = ''
    if category == 'Other':
        flag = 'NEEDS_REVIEW'
        category_reasons.append('unrecognized issue')

    # 2. Priority mapping
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_severities = [kw for kw in severity_keywords if kw in desc_lower]
    
    if found_severities:
        priority = 'Urgent'
        reason = f"Category is {category} because of '{category_reasons[0]}' and Priority is Urgent because description contains '{found_severities[0]}'."
    else:
        priority = 'Standard'
        reason = f"Category is {category} because description mentions '{category_reasons[0]}'."

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
    """
    results = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                row.update(classified)
                results.append(row)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                
    if not results:
        print("No results to write.")
        return

    fieldnames = list(results[0].keys())
    
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
