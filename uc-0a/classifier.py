"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    # 1 & 2. Enforcement: Priorities & Severity keywords
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    priority = 'Standard'
    for kw in severity_keywords:
        if kw in desc:
            priority = 'Urgent'
            break
            
    # Enforcement Categories mapping
    categories_map = {
        'Pothole': ['pothole', 'tyre damage'],
        'Flooding': ['flood', 'rain', 'water'],
        'Streetlight': ['streetlight', 'light', 'dark', 'sparking'],
        'Waste': ['garbage', 'waste', 'animal', 'trash'],
        'Noise': ['music', 'noise', 'loud'],
        'Road Damage': ['road surface', 'crack', 'sinking', 'manhole', 'broken', 'footpath', 'tiles'],
        'Heritage Damage': ['heritage', 'monument'],
        'Heat Hazard': ['heat'],
        'Drain Blockage': ['drain', 'clog', 'blockage']
    }
    
    matched_categories = set()
    for cat, keywords in categories_map.items():
        for kw in keywords:
            if kw in desc:
                matched_categories.add(cat)
                
    # 4. Enforcement: Ambiguity -> NEEDS_REVIEW
    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
        flag = ''
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        
    # 3. Enforcement: reason must be exactly one sentence citing specific words
    sentences = [s.strip() + '.' for s in re.split(r'[.!?]+', row.get('description', '')) if s.strip()]
    reason_sentence = sentences[0] if sentences else "No description provided."
    for s in sentences:
        s_lower = s.lower()
        if any(kw in s_lower for kw in severity_keywords) or \
           any(kw in s_lower for kws in categories_map.values() for kw in kws):
            reason_sentence = s
            break
            
    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason_sentence,
        'flag': flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if not row.get('description'):
                        results.append({
                            'complaint_id': row.get('complaint_id', 'Unknown'),
                            'category': 'Other',
                            'priority': 'Low',
                            'reason': 'Description is null or empty.',
                            'flag': 'NEEDS_REVIEW'
                        })
                        continue
                        
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    results.append({
                        'complaint_id': row.get('complaint_id', 'Unknown'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': f'System error during processing: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })
    except Exception as read_err:
        print(f"Failed to read input file: {read_err}")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as write_err:
        print(f"Failed to write output file: {write_err}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
