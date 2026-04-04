"""
UC-0A — Complaint Classifier
Implemented based on RICE enforcement parameters from agents.md and skills.md.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on strictly defined schema and keywords.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '')
    desc_lower = description.lower()
    
    # 1. Evaluate Priority based on exact severity keywords
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = 'Standard'
    matched_urgent_kw = None
    
    for kw in urgent_keywords:
        if kw in desc_lower:
            priority = 'Urgent'
            matched_urgent_kw = kw
            break
            
    # 2. Evaluate Category based on mapping
    category_map = {
        'Pothole': ['pothole'],
        'Flooding': ['flood', 'rain', 'waterlogged'],
        'Streetlight': ['light', 'dark', 'sparking', 'streetlight', 'lamp'],
        'Waste': ['waste', 'garbage', 'animal', 'smell', 'bin'],
        'Noise': ['noise', 'music', 'loud', 'sound'],
        'Road Damage': ['crack', 'sinking', 'broken', 'repair'],
        'Heritage Damage': ['heritage', 'monument'],
        'Heat Hazard': ['hot', 'heat'],
        'Drain Blockage': ['drain', 'manhole', 'sewer']
    }
    
    found_categories = set()
    matched_cat_kw = None
    for cat, kws in category_map.items():
        for kw in kws:
            if kw in desc_lower:
                found_categories.add(cat)
                matched_cat_kw = kw
                break
                
    # 3. Resolve Ambiguity (Enforcement Rule 4)
    if len(found_categories) == 1:
        category = list(found_categories)[0]
        flag = ""
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        # No categories found
        category = "Other"
        flag = ""
        
    # 4. Generate Reason referencing specific parsed words (Enforcement Rule 3)
    cited_word = matched_urgent_kw if matched_urgent_kw else (matched_cat_kw if matched_cat_kw else "unclear issue")
    reason = f"Classified based on the specific presence of '{cited_word}' in the description."

    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row gracefully, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                # Fallback implementation on row error to prevent crash
                writer.writerow({
                    'complaint_id': row.get('complaint_id', 'ERROR'),
                    'category': 'Other',
                    'priority': 'Low',
                    'reason': 'Unexpected processing error occurred.',
                    'flag': 'NEEDS_REVIEW'
                })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
