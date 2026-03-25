"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based strictly on the RICE prompt 
    from agents.md and skills.md.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = str(row.get('description', '')).lower()
    
    # RICE Priority Rule: Urgent if severity keywords presentt
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    priority_reason = ""
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            priority_reason = f"contains severity keyword '{kw}'"
            break
            
    # RICE Category Rule
    # Exact allowed categories: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    category_map = {
        'Pothole': ['pothole'],
        'Flooding': ['flood', 'knee-deep', 'water'],
        'Streetlight': ['streetlight', 'lights', 'dark', 'sparking'],
        'Waste': ['garbage', 'waste', 'smell', 'animal', 'dumped'],
        'Noise': ['music', 'noise', 'loud'],
        'Road Damage': ['road surface', 'crack', 'broken', 'manhole', 'tiles broken', 'sinking'],
        'Heritage Damage': ['heritage'],
        'Heat Hazard': ['heat', 'sun'],
        'Drain Blockage': ['drain block', 'drain', 'clog']
    }
    
    matched_categories = set()
    category_reasons = []
    
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in desc:
                matched_categories.add(cat)
                category_reasons.append(kw)
    
    flag = ""
    reason = ""
    
    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
        reason = f"Matched explicit keyword '{category_reasons[0]}' for {category}."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous/Multiple keywords found: {', '.join(category_reasons)}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No explicit category keywords found. Insufficient context."
        
    if priority == "Urgent":
        reason += f" Priority is Urgent because it {priority_reason}."
        
    return {
        'category': category,
        'priority': priority,
        'reason': reason.strip(),
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        # Ensure our new classification fields exist in the output headers
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        for field in ['category', 'priority', 'reason', 'flag']:
            if field not in fieldnames:
                fieldnames.append(field)
                
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            try:
                # Skill 1: classify_complaint
                classification = classify_complaint(row)
                row.update(classification)
            except Exception as e:
                # Error handling: Flags nulls, does not crash on bad rows
                row['category'] = "Other"
                row['priority'] = "Standard"
                row['reason'] = f"Failed to process: {str(e)}"
                row['flag'] = "NEEDS_REVIEW"
                
            writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
