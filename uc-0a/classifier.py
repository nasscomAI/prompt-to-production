"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
CATEGORIES = ['Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to RICE enforcement rules.
    """
    desc = str(row.get('description', '')).lower()
    
    # Priority Identification
    found_sev_kws = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    priority = 'Urgent' if found_sev_kws else 'Standard'
            
    # Category Identification
    cats = set()
    if 'pothole' in desc: cats.add('Pothole')
    if 'flood' in desc: cats.add('Flooding')
    if 'streetlight' in desc or 'lights out' in desc or 'dark' in desc: cats.add('Streetlight')
    if 'waste' in desc or 'garbage' in desc or 'dump' in desc or 'dead animal' in desc: cats.add('Waste')
    if 'music' in desc or 'noise' in desc: cats.add('Noise')
    if 'crack' in desc or 'sink' in desc or 'manhole' in desc or 'broken' in desc or 'tile' in desc or 'footpath' in desc: cats.add('Road Damage')
    if 'heritage' in desc: cats.add('Heritage Damage')
    if 'heat' in desc: cats.add('Heat Hazard')
    if 'drain' in desc: cats.add('Drain Blockage')
        
    flag = ''
    if len(cats) == 1:
        category = list(cats)[0]
    elif len(cats) > 1:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        
    # Reason Generation citing specific words
    sentences = re.split(r'[.!?]', row.get('description', ''))
    first_sentence = sentences[0].strip() if sentences else "No valid description"
    
    if priority == 'Urgent':
        reason = f"Urgent priority due to severity words: {', '.join(found_sev_kws)}. Context matches: '{first_sentence}'"
    elif flag == 'NEEDS_REVIEW':
        if len(cats) > 1:
            reason = f"Ambiguous due to multiple category hints ({', '.join(cats)}). Mentioned: '{first_sentence}'"
        else:
            reason = f"Review required because it does not match known categories. Mentioned: '{first_sentence}'"
    else:
        reason = f"Classified as {category}. Text explicitly mentions: '{first_sentence}'"

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
    Flags nulls and handles exceptions without crashing.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if not row or not row.get('description') or not row.get('description').strip():
                    results.append({
                        'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': 'Row missing description completely.',
                        'flag': 'NULL_ROW'
                    })
                else:
                    results.append(classify_complaint(row))
            except Exception as e:
                results.append({
                    'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                    'category': 'Other',
                    'priority': 'Low',
                    'reason': f"Error processing row: {e}",
                    'flag': 'ERROR'
                })

    if results:
        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
