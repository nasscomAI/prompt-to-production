"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

import re

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def get_category_and_flag(desc):
    d = desc.lower()
    cats = []
    if 'pothole' in d: cats.append('Pothole')
    if 'flood' in d: cats.append('Flooding')
    if 'streetlight' in d or 'lights out' in d or 'dark' in d: cats.append('Streetlight')
    if 'garbage' in d or 'waste' in d: cats.append('Waste')
    if 'music' in d or 'noise' in d: cats.append('Noise')
    if 'road surface' in d or 'footpath tiles' in d: cats.append('Road Damage')
    if 'heritage' in d: cats.append('Heritage Damage')
    if 'heat' in d: cats.append('Heat Hazard')
    if 'drain' in d or 'manhole' in d: cats.append('Drain Blockage')
    
    if len(cats) == 1:
        return cats[0], ""
    elif len(cats) > 1:
        return 'Other', "NEEDS_REVIEW"
    else:
        return 'Other', "NEEDS_REVIEW"

def classify_complaint(row: dict) -> dict:
    description = row.get('description', '')
    d_lower = description.lower()
    
    priority = "Standard"
    urgent_kw = None
    for keyword in SEVERITY_KEYWORDS:
        if keyword in d_lower:
            priority = "Urgent"
            urgent_kw = keyword
            break
        
    cat, flag = get_category_and_flag(d_lower)
    
    # Extract strictly one sentence citing the specific trigger words
    sentences = re.split(r'(?<=[.!?])\s+', description)
    reason = ""
    
    if urgent_kw:
        for s in sentences:
            if urgent_kw in s.lower():
                reason = s.strip()
                break
    else:
        for s in sentences:
            cat_words = ['pothole', 'flood', 'streetlight', 'lights out', 'garbage', 'waste', 'music', 'noise', 'road surface', 'footpath tiles', 'heritage', 'heat', 'drain', 'manhole']
            if any(cw in s.lower() for cw in cat_words):
                reason = s.strip()
                break
                
    if not reason:
        reason = sentences[0].strip() if sentences else description.strip()
        
    output = dict(row)
    output.pop('category', None)
    output.pop('priority_flag', None)
    output['category'] = cat
    output['priority'] = priority
    output['reason'] = reason
    output['flag'] = flag
    return output


def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        fieldnames = [f for f in reader.fieldnames if f not in ('category', 'priority_flag')]
        fieldnames.extend(['category', 'priority', 'reason', 'flag'])
        rows = list(reader)
        
    for row in rows:
        row.update(classify_complaint(row))
        
    with open(output_path, 'w', encoding='utf-8', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
