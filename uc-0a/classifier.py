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
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '').lower()
    
    if not description:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Standard',
            'reason': 'No description provided.',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Define category keywords
    category_keywords = {
        'Pothole': ['pothole'],
        'Flooding': ['flood', 'water', 'drain'],
        'Streetlight': ['streetlight', 'light', 'unlit', 'lighting'],
        'Waste': ['waste', 'garbage', 'cleared', 'not cleared'],
        'Noise': ['noise', 'music', 'audible', 'sound'],
        'Road Damage': ['road', 'damage', 'tarmac', 'melting', 'surface'],
        'Heritage Damage': ['heritage', 'night market'],
        'Heat Hazard': ['heat', 'temperature', 'hot', 'dangerous temperatures'],
        'Drain Blockage': ['drain', 'blockage'],
    }
    
    category = 'Other'
    matched_word = ''
    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in description:
                category = cat
                matched_word = kw
                break
        if category != 'Other':
            break
    
    # Priority
    priority_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = 'Standard'
    for kw in priority_keywords:
        if kw in description:
            priority = 'Urgent'
            break
    
    # Reason
    if category != 'Other':
        reason = f"The description mentions '{matched_word}' which indicates {category}."
    else:
        reason = "The description does not clearly match any specific category."
    
    # Flag
    flag = 'NEEDS_REVIEW' if category == 'Other' else ''
    
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
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # On error, add a failed entry
                    results.append({
                        'complaint_id': row.get('complaint_id', 'unknown'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': f'Error processing row: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
    
    # Write output
    if results:
        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
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
