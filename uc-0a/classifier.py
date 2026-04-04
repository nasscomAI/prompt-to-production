"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

VALID_CATEGORIES = [
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage'
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    priority = 'Standard'
    reason = "Issue reported in description."
    
    # Priority logic: Urgent if severity keywords present
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = 'Urgent'
            break
            
    # Category logic
    matched_cats = []
    if 'pothole' in desc or 'tyre' in desc:
        matched_cats.append('Pothole')
    if 'flood' in desc or 'water' in desc:
        matched_cats.append('Flooding')
    if 'streetlight' in desc or 'sparking' in desc or 'dark' in desc:
        matched_cats.append('Streetlight')
    if 'garbage' in desc or 'waste' in desc or 'animal' in desc or 'smell' in desc:
        matched_cats.append('Waste')
    if 'noise' in desc or 'music' in desc:
        matched_cats.append('Noise')
    if 'road' in desc and ('crack' in desc or 'sinking' in desc or 'break' in desc or 'broken' in desc):
        matched_cats.append('Road Damage')
    if 'heritage' in desc or 'monument' in desc:
        matched_cats.append('Heritage Damage')
    if 'heat' in desc or 'sun' in desc:
        matched_cats.append('Heat Hazard')
    if 'drain' in desc or 'manhole' in desc or 'block' in desc:
        matched_cats.append('Drain Blockage')
        
    # Handling conflict/ambiguity
    # Some combinations make sense to filter, e.g., 'road' and 'pothole'
    if 'Pothole' in matched_cats and 'Road Damage' in matched_cats:
        matched_cats.remove('Road Damage')
    if 'Flooding' in matched_cats and 'Drain Blockage' in matched_cats:
        # Often flooding is caused by drain, prefer Flooding
        matched_cats.remove('Drain Blockage')
    
    if len(matched_cats) == 1:
        category = matched_cats[0]
        flag = ''
    elif len(matched_cats) > 1:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        
    # Reason logic: one sentence, citing specifically words from description
    # We will find the shortest full sentence that contains a categorical or severity indication.
    sentences = re.split(r'(?<=[.!?]) +', row.get('description', ''))
    reason_sentence = sentences[0] if sentences else ""
    
    # ensure citation
    cited_words = []
    for word in desc.split():
        clean_word = word.strip('.,!?"')
        if len(clean_word) > 4:
            cited_words.append(clean_word)
            break
            
    if cited_words:
         reason = f"Classified based on description mentioning '{cited_words[0]}': {reason_sentence}"
    else:
         reason = f"Classified from description: {reason_sentence}"
         
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            rows = list(reader)
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return
        
    results = []
    for row in rows:
        try:
            res = classify_complaint(row)
            out_row = dict(row) # keep original data
            out_row['category'] = res['category']
            out_row['priority'] = res['priority']
            out_row['reason'] = res['reason']
            out_row['flag'] = res['flag']
            results.append(out_row)
        except Exception as e:
            print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")
            out_row = dict(row)
            out_row['category'] = 'Other'
            out_row['priority'] = 'Standard'
            out_row['reason'] = f"Error during classification: {e}"
            out_row['flag'] = 'ERROR'
            results.append(out_row)
            
    if results:
        try:
            with open(output_path, 'w', encoding='utf-8', newline='') as fout:
                fieldnames = results[0].keys()
                writer = csv.DictWriter(fout, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
