"""

UC-0A — Complaint  Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    
    # Priority logic
    priority = 'Standard'
    reason_word = ''
    for word in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', description):
            priority = 'Urgent'
            reason_word = word
            break
            
    # Category logic mapping
    category_mapping = {
        'Pothole': ['pothole', 'crater'],
        'Drain Blockage': ['drain blocked', 'drain', 'choked'],
        'Flooding': ['flood', 'flooded', 'waterlogged'],
        'Streetlight': ['streetlight', 'lights out', 'dark'],
        'Waste': ['garbage', 'dump', 'waste', 'trash', 'dead animal'],
        'Noise': ['music', 'loud', 'noise', 'party'],
        'Road Damage': ['cracked', 'sinking', 'manhole', 'tiles broken', 'broken'],
        'Heritage Damage': ['heritage monument', 'fort damaged'],
        'Heat Hazard': ['heatwave', 'boiling']
    }
    
    assigned_category = 'Other'
    flag = ''
    match_count = 0
    
    for cat, keywords in category_mapping.items():
        for kw in keywords:
            if kw in description:
                assigned_category = cat
                match_count += 1
                if not reason_word:
                    reason_word = kw
                break
                
    # Ambiguity check
    if match_count > 1 or assigned_category == 'Other':
        flag = 'NEEDS_REVIEW'
        if assigned_category == 'Other':
            assigned_category = 'Other'
            
    # Reason fallback
    if not reason_word:
        reason_word = 'unclear'
        
    reason = f"The description contained the word '{reason_word}'."

    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': assigned_category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    fieldnames = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Retain original fields plus the 4 new ones minus complaint_id if it's already there
            fieldnames = list(reader.fieldnames)
            for f_add in ['category', 'priority', 'reason', 'flag']:
                if f_add not in fieldnames:
                    fieldnames.append(f_add)
                    
            for row in reader:
                try:
                    classification_res = classify_complaint(row)
                    row.update(classification_res)
                    results.append(row)
                except Exception as e:
                    row['category'] = 'Other'
                    row['priority'] = 'Low'
                    row['reason'] = f"Failed to process: {str(e)}"
                    row['flag'] = 'NEEDS_REVIEW'
                    results.append(row)
                    
    except Exception as e:
        print(f"Error opening input file: {e}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
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
