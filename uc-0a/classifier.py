import argparse
import csv
import re
import traceback

CATEGORY_MAPPING = {
    'Pothole': ['pothole', 'potholes'],
    'Flooding': ['flood', 'flooded', 'flooding', 'waterlogging', 'knee-deep'],
    'Streetlight': ['streetlight', 'light', 'lights', 'dark'],
    'Waste': ['waste', 'garbage', 'trash', 'dumped', 'dump'],
    'Noise': ['noise', 'loud', 'music', 'sound'],
    'Road Damage': ['crack', 'cracked', 'sinking', 'broken', 'upturned'],
    'Heritage Damage': ['heritage', 'monument'],
    'Heat Hazard': ['heat'],
    'Drain Blockage': ['drain', 'clog', 'sewage']
}

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on instructions from agents.md.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = str(row.get('description', '')).lower()
    
    if not desc.strip():
        return {
            'category': 'Other',
            'priority': 'Low',
            'reason': 'The description is empty.',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Find matching categories
    matched_cats = set()
    category_match_word = ""

    for cat_name, kw_list in CATEGORY_MAPPING.items():
        for kw in kw_list:
            # We check both word boundaries and substrings for robustness
            if re.search(r'\b' + re.escape(kw) + r'\b', desc) or kw in desc:
                matched_cats.add(cat_name)
                if not category_match_word:
                    category_match_word = kw
    
    # Determine Ambiguity (0 or >1 categories matched)
    ambiguous = len(matched_cats) != 1
    category = list(matched_cats)[0] if len(matched_cats) == 1 else 'Other'

    # Determine Severity
    urgent = False
    severity_match_word = ""
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc) or kw in desc:
            urgent = True
            severity_match_word = kw
            break
            
    # Apply Enforcement Rules from agents.md
    if ambiguous:
        flag = 'NEEDS_REVIEW'
        priority = 'Low'
    else:
        flag = ''
        priority = 'Urgent' if urgent else 'Standard'
        
    # Reason formatting
    if ambiguous:
        if len(matched_cats) == 0:
            reason = "The description lacked clear matching keywords and could not be determined."
        else:
            reason = f"The description matched multiple categories ({', '.join(matched_cats)}) causing genuine ambiguity."
    elif urgent:
        reason = f"The description contained '{category_match_word}' confirming the category, and specifically quoted '{severity_match_word}' triggering Urgent priority."
    else:
        reason = f"The description specifically contained '{category_match_word}' confirming the category, with no severe keywords."

    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, and produce output even if some rows fail.
    """
    results = []
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            fn = reader.fieldnames
            fieldnames = [name for name in fn] if fn is not None else []
            
            # Ensure our output fields exist
            for f in ['category', 'priority', 'reason', 'flag']:
                if f not in fieldnames:
                    fieldnames.append(f)
                    
            for row in reader:
                try:
                    if not row or 'description' not in row:
                        row['flag'] = 'NEEDS_REVIEW'
                        row['category'] = 'Other'
                        row['priority'] = 'Low'
                        row['reason'] = 'Malformed row data.'
                    else:
                        classification = classify_complaint(row)
                        row.update(classification)
                except Exception as e:
                    # Not crashing on bad rows!
                    row['flag'] = 'NEEDS_REVIEW'
                    row['category'] = 'Other'
                    row['priority'] = 'Low'
                    row['reason'] = f"Exception during classification: {str(e)}"
                
                results.append(row)
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
        return

    # Write output properly
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
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
