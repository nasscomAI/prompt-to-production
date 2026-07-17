"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', '')
    
    category = "Other"
    flag = "NEEDS_REVIEW"
    
    # Simple rule-based classification based on keywords
    if 'pothole' in desc:
        category = "Pothole"
        flag = ""
    elif 'flood' in desc:
        category = "Flooding"
        flag = ""
    elif 'streetlight' in desc or 'lights out' in desc:
        category = "Streetlight"
        flag = ""
    elif 'garbage' in desc or 'waste' in desc:
        category = "Waste"
        flag = ""
    elif 'music' in desc or 'noise' in desc or 'loud' in desc:
        category = "Noise"
        flag = ""
    elif 'cracked' in desc or 'tiles broken' in desc:
        category = "Road Damage"
        flag = ""
    elif 'heritage' in desc and 'damage' in desc:
        category = "Heritage Damage"
        flag = ""
    elif 'heat' in desc:
        category = "Heat Hazard"
        flag = ""
    elif 'drain block' in desc:
        category = "Drain Blockage"
        flag = ""
        
    priority = "Standard"
    found_severe_kw = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            found_severe_kw = kw
            break
            
    if category == "Other":
        reason = "Category is ambiguous and needs review."
    else:
        if priority == "Urgent":
            reason = f"Classified as {category} and marked Urgent due to keyword '{found_severe_kw}'."
        else:
            reason = f"Classified as {category} based on description."
            
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        for row in reader:
            try:
                res = classify_complaint(row)
                # Merge original row with classification results
                merged = {**row, **res}
                results.append(merged)
            except Exception as e:
                # Handle error gracefully
                row['category'] = 'Error'
                row['priority'] = 'Error'
                row['reason'] = str(e)
                row['flag'] = 'NEEDS_REVIEW'
                results.append(row)
                
    if not results:
        return
        
    # Determine new fieldnames
    new_fieldnames = list(fieldnames)
    for key in ['category', 'priority', 'reason', 'flag']:
        if key not in new_fieldnames:
            new_fieldnames.append(key)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
