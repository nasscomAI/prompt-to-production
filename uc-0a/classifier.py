"""
UC-0A — Complaint Classifier
Implemented using RICE enforcements from agents.md/skills.md.
Rule-based keyword matching enforces taxonomy, severity, reason, flag.
"""
import argparse
import csv
import re
from typing import Dict, List

# Schema enforcements
CATEGORIES = [
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 'Road Damage',
    'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
]
URGENT_KEYWORDS = {
    'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard',
    'fell', 'collapse', 'hospitalised', 'risk', 'unsafe'
}

CATEGORY_KEYWORDS = {
    'Pothole': {'pothole', 'crater', 'hole', 'sinkhole'},
    'Flooding': {'flood', 'waterlogged', 'submerged'},
    'Streetlight': {'streetlight', 'light', 'unlit', 'dark', 'flicker', 'spark'},
    'Waste': {'garbage', 'waste', 'overflow', 'bin', 'dump'},
    'Noise': {'music', 'noise', 'drilling', 'loud'},
    'Road Damage': {'road.*damage', 'crack', 'sinking', 'buckle', 'broken surface', 'tarmac'},
    'Heritage Damage': {'heritage', 'historic', 'old city'},
    'Heat Hazard': {'heat', 'melting', 'temperature', 'burn'},
    'Drain Blockage': {'drain.*block', 'clog', 'mosquito'},
    'Other': set()
}

def classify_complaint(row: Dict) -> Dict:
    """
    Classify single complaint using keyword rules from RICE enforcements.
    """
    description = row['description'].lower()
    matches = []
    
    # Category matching
    for cat, words in CATEGORY_KEYWORDS.items():
        for word in words:
            if re.search(word, description):
                matches.append(cat)
                break
    
    if len(matches) == 0:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
    elif len(matches) == 1:
        category = matches[0]
        flag = ''
    else:
        category = max(set(matches), key=matches.count)  # Most specific
        flag = 'NEEDS_REVIEW' if len(matches) > 1 else ''
    
    # Priority
    urgent = any(word in description for word in URGENT_KEYWORDS)
    priority = 'Urgent' if urgent else 'Standard'  # Default Standard, no Low for simplicity
    
    # Reason
    key_phrases = [phrase for cat, phrases in CATEGORY_KEYWORDS.items() for phrase in phrases if re.search('|'.join(phrases), description)][:3]
    reason = f"Matches '{category.lower()}' due to keywords: {', '.join(key_phrases[:3]) if key_phrases else 'general description'}."
    
    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Batch process CSV.
    """
    with open(input_path, 'r') as infile, open(output_path, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            try:
                classification = classify_complaint(row)
                row.update(classification)
                writer.writerow(row)
            except Exception as e:
                row.update({'category': 'Other', 'priority': 'Low', 'reason': f'Error: {e}', 'flag': 'NEEDS_REVIEW'})
                writer.writerow(row)
    print(f"Classification complete. Output: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)

