"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    
    # Priority schema - Urgent if severity keywords present
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = any(kw in description for kw in severity_keywords)
    priority = 'Urgent' if is_urgent else 'Standard'
    
    # Category schema - Needs to match exact strings (no variations)
    category_mapping = {
        'pothole': 'Pothole',
        'flood': 'Flooding',
        'waterlogging': 'Flooding',
        'light': 'Streetlight',
        'dark': 'Streetlight',
        'waste': 'Waste',
        'garbage': 'Waste',
        'trash': 'Waste',
        'bin': 'Waste',
        'noise': 'Noise',
        'music': 'Noise',
        'road': 'Road Damage',
        'crack': 'Road Damage',
        'heritage': 'Heritage Damage',
        'heat': 'Heat Hazard',
        'drain': 'Drain Blockage',
        'manhole': 'Drain Blockage',
        'animal': 'Other', 
        'footpath': 'Road Damage' 
    }
    
    matched_cats = set()
    for kw, cat in category_mapping.items():
        if kw in description:
            matched_cats.add(cat)
            
    if 'heritage' in description and 'light' in description:
        # Avoid false confidence on ambiguity between "Heritage Damage" & "Streetlight"
        matched_cats = set(['Heritage Damage', 'Streetlight'])
            
    if len(matched_cats) == 1:
        category = list(matched_cats)[0]
        flag = ''
    elif len(matched_cats) > 1:
        category = 'Other'
        flag = 'NEEDS_REVIEW' # False confidence on ambiguity (genuinely ambiguous)
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'

    # Extracting Reason (One sentence citing specific words from description)
    sentences = [s.strip() for s in re.split(r'[.!?]\s*', row.get('description', '')) if s.strip()]
    if sentences:
        reason = f"The description explicitly mentions '{sentences[0]}'."
    else:
        reason = "The description provided no clear context."
        
    return {
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
        with open(input_path, 'r', encoding='utf-8') as fin, \
             open(output_path, 'w', encoding='utf-8', newline='') as fout:
            
            reader = csv.DictReader(fin)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("Input CSV is empty or has no headers.")
            
            # Remove existing classification columns if they mistakenly exist in input
            for col in ['category', 'priority', 'reason', 'flag']:
                if col in fieldnames:
                    fieldnames.remove(col)
                    
            output_fields = fieldnames + ['category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(fout, fieldnames=output_fields)
            writer.writeheader()
            
            for row in reader:
                try:
                    if not row.get('description'):
                        # Handle nulls
                        classification = {
                            'category': 'Other', 'priority': 'Low', 
                            'reason': 'Description is empty or null.', 'flag': 'NEEDS_REVIEW'
                        }
                    else:
                        classification = classify_complaint(row)
                    
                    # Update row and retain original columns properly
                    out_row = {k: v for k, v in row.items() if k in fieldnames}
                    out_row.update(classification)
                    writer.writerow(out_row)
                    
                except Exception as e:
                    # Not crash on bad rows
                    out_row = {k: v for k, v in row.items() if k in fieldnames}
                    out_row.update({
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f"Failed to classify: {str(e)}",
                        'flag': 'ERROR'
                    })
                    writer.writerow(out_row)
                    
    except Exception as e:
        print(f"Error processing batch: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
