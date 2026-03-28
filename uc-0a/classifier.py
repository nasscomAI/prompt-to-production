"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '')
    desc_lower = description.lower()
    
    # 1. Enforce category matching
    categories = {
        'pothole': 'Pothole',
        'flood': 'Flooding',
        'streetlight': 'Streetlight',
        'light': 'Streetlight',
        'waste': 'Waste',
        'garbage': 'Waste',
        'noise': 'Noise',
        'music': 'Noise',
        'road damage': 'Road Damage',
        'cracked': 'Road Damage',
        'heritage': 'Heritage Damage',
        'heat': 'Heat Hazard',
        'drain block': 'Drain Blockage',
        'drain blocked': 'Drain Blockage'
    }
    
    category = 'Other'
    flag = 'NEEDS_REVIEW'
    matched_word = None
    
    for key, val in categories.items():
        if key in desc_lower:
            category = val
            flag = '' # Not ambiguous anymore
            matched_word = key
            break
            
    # 2. Enforce priority rules
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = 'Standard'
    severity_reason = None
    
    for keyword in severity_keywords:
        if keyword in desc_lower:
            priority = 'Urgent'
            severity_reason = keyword
            break
            
    # 3. Formulate the reason citing specific words
    if severity_reason and matched_word:
        reason = f"Classified as {category} with Urgent priority due to the presence of '{matched_word}' and '{severity_reason}'."
    elif severity_reason:
        reason = f"Priority marked Urgent due to mention of '{severity_reason}' in the complaint."
    elif matched_word:
        reason = f"Categorized based on the specific mentioning of the word '{matched_word}'."
    else:
        reason = "The description was ambiguous requiring manual categorization."

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
    """
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
    results = []
    for row in rows:
        try:
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            # Must: flag nulls, not crash on bad rows, produce output even if some rows fail
            print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")
            results.append({
                'complaint_id': row.get('complaint_id', ''),
                'category': 'Other',
                'priority': 'Low',
                'reason': f'Failed processing due to error: {e}',
                'flag': 'NEEDS_REVIEW'
            })
            
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input = os.path.join(script_dir, "..", "data", "city-test-files", "test_pune.csv")
    default_output = os.path.join(script_dir, "results_pune.csv")
    
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  default=default_input, help="Path to test_[city].csv")
    parser.add_argument("--output", default=default_output, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
    
   
     