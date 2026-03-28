"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based strictly on rules in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', '')
    
    priority = "Standard"
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_urgent = [kw for kw in urgent_keywords if kw in description]
    if matched_urgent:
        priority = "Urgent"

    cat_keywords = {
        'Pothole': ['pothole'],
        'Drain Blockage': ['drain', 'manhole'],
        'Flooding': ['flood'],
        'Heritage Damage': ['heritage'],
        'Streetlight': ['streetlight', 'light', 'dark'],
        'Waste': ['waste', 'garbage', 'smell', 'animal', 'dump'],
        'Noise': ['noise', 'music', 'loud'],
        'Road Damage': ['road surface', 'crack', 'sink', 'footpath', 'tile'],
        'Heat Hazard': ['heat']
    }
    
    matched_cats = []
    matched_words = {}
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in description:
                matched_cats.append(cat)
                matched_words[cat] = kw
                break
                
    category = "Other"
    word = ""
    flag = ""
    
    if len(matched_cats) == 1:
        category = matched_cats[0]
        word = matched_words[category]
    elif len(matched_cats) > 1:
        if 'Heritage Damage' in matched_cats:
            category = 'Heritage Damage'
            word = matched_words[category]
        elif 'Drain Blockage' in matched_cats and 'Flooding' in matched_cats:
            category = 'Drain Blockage'
            word = matched_words[category]
        else:
            category = matched_cats[0]
            word = matched_words[category]
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    if flag == "NEEDS_REVIEW":
        if priority == "Urgent":
            reason = f"The description is ambiguous but marked Urgent due to '{matched_urgent[0]}'."
        else:
            reason = "The description lacks clear categorization keywords and must be reviewed."
    else:
        if priority == "Urgent":
            reason = f"The word '{word}' places this in {category}, and it is Urgent due to '{matched_urgent[0]}'."
        else:
            reason = f"The description justifies the {category} category due to the word '{word}'."

    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return False
        
    results = []
    for row in rows:
        try:
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            results.append({
                'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                'category': 'Other',
                'priority': 'Low',
                'reason': f"Processing error: {str(e)}",
                'flag': 'NEEDS_REVIEW'
            })
            
    with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    success = batch_classify(args.input, args.output)
    if success:
        print(f"Done. Results written to {args.output}")
