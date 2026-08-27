"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    # Priority Enforcement
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_sev = [kw for kw in severity_keywords if kw in desc]
    
    if matched_sev:
        priority = "Urgent"
        priority_reason = f"contains severity keyword '{matched_sev[0]}'"
    else:
        priority = "Standard"
        priority_reason = "does not contain severity keywords"
        
    # Category Enforcement (Exact matching rules)
    cat_keywords = {
        'Pothole': ['pothole', 'crater'],
        'Flooding': ['flood', 'flooded', 'floods', 'waterlogging'],
        'Streetlight': ['streetlight', 'light', 'dark', 'sparking'],
        'Waste': ['waste', 'garbage', 'dead animal', 'dump'],
        'Noise': ['noise', 'music', 'loud'],
        'Road Damage': ['crack', 'sinking', 'broken', 'footpath', 'manhole'],
        'Heritage Damage': ['heritage damage', 'monument'],
        'Heat Hazard': ['heat ', 'hot'],
        'Drain Blockage': ['drain block', 'drain blocked', 'drain']
    }
    
    matched_categories = []
    matched_cat_kws = []
    
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in desc:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_cat_kws.append(kw)
                    break # avoid multiple keywords for same category inflating the matches
                    
    flag = ''
    category = 'Other'
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        cat_reason = f"it mentions the keyword '{matched_cat_kws[0]}'"
    elif len(matched_categories) > 1:
        flag = 'NEEDS_REVIEW'
        cat_reason = f"ambiguous as it matches multiple categories ({', '.join(matched_categories)})"
    else:
        flag = 'NEEDS_REVIEW'
        cat_reason = "no specific exact category keyword was found"
        
    # Exact Output Enforcement
    reason = f"The category is {category} because {cat_reason}, and priority is {priority} because it {priority_reason}."
    
    row['category'] = category
    row['priority'] = priority
    row['reason'] = reason
    row['flag'] = flag
    
    return row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8', newline='') as fout:
             
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        for new_field in ['category', 'priority', 'reason', 'flag']:
            if new_field not in fieldnames:
                fieldnames.append(new_field)
                
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            try:
                classified_row = classify_complaint(row)
                writer.writerow(classified_row)
            except Exception as e:
                # Flag row and handle error, allowing batch to proceed without crashing
                row['flag'] = 'NEEDS_REVIEW'
                row['reason'] = f"Error during processing: {str(e)}"
                if 'category' not in row: row['category'] = 'Other'
                if 'priority' not in row: row['priority'] = 'Standard'
                writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
