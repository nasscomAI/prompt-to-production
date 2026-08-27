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
    description = str(row.get('description', '')).lower()
    complaint_id = row.get('complaint_id', '')

    if not description or description.strip() == '':
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'The description is empty.',
            'flag': 'NEEDS_REVIEW'
        }

    # 1. Evaluate Priority
    # "injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = 'Standard'
    urgent_found = [kw for kw in urgent_keywords if kw in description]
    if urgent_found:
        priority = 'Urgent'
        

    # 2. Evaluate Category
    # "Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
    category_keywords = {
        'Pothole': ['pothole', 'crater'],
        'Flooding': ['flood', 'water', 'submerged', 'inundation', 'drain overflow'],
        'Streetlight': ['streetlight', 'light', 'dark', 'bulb', 'unlit', 'wiring'],
        'Waste': ['waste', 'garbage', 'trash', 'rubbish', 'dump', 'bin'],
        'Noise': ['noise', 'loud', 'music', 'sound'],
        'Road Damage': ['road', 'damage', 'crack', 'surface', 'subsidence', 'paving', 'tarmac'],
        'Heritage Damage': ['heritage', 'monument', 'statue', 'temple', 'ancient'],
        'Heat Hazard': ['heat', 'burn', 'temperature', '°c', 'sun', 'melting'],
        'Drain Blockage': ['drain', 'clog', 'block', 'overflow', 'sewer']
    }

    matched_categories = []
    category_words = []
    
    for cat, kws in category_keywords.items():
        for kw in kws:
            if kw in description:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                category_words.append(kw)

    flag = ''
    if len(matched_categories) >= 1:
        category = matched_categories[0]
        word = next(kw for kw in category_keywords[category] if kw in description)
        reason = f'Assigned category {category} as the description contains the word "{word}".'
        if len(matched_categories) > 1:
            reason += f' (Also noticed keywords for other categories but it is still valid).'
    else:
        # Unmentioned
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        reason = 'Could not determine category as no specific keywords were found.'

    # Adjust reason to include priority justification
    if priority == 'Urgent':
        word = urgent_found[0]
        reason = reason[:-1] + f' and marked Urgent due to severity keyword "{word}".'

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
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    # Not crashing on bad rows
                    results.append({
                        'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f'Error processing row: {str(e)}.',
                        'flag': 'NEEDS_REVIEW'
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
        
    if not results:
        print("No valid rows to write.")
        return

    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
