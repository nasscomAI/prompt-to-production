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
    desc = row.get("description", "")
    if not desc:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = desc.lower()
    
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    priority = "Standard"
    matched_sev = None
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            matched_sev = kw
            break
            
    category_keywords = {
        'Pothole': ['pothole', 'crater'],
        'Flooding': ['flood', 'waterlogging', 'floods'],
        'Streetlight': ['streetlight', 'lights out', 'dark', 'lamp'],
        'Waste': ['waste', 'garbage', 'trash', 'animal'],
        'Noise': ['noise', 'loud', 'music', 'speaker'],
        'Road Damage': ['cracked', 'broken', 'uneven', 'surface cracked', 'tiles broken', 'road surface', 'footpath'],
        'Heritage Damage': ['heritage', 'monument', 'historic'],
        'Heat Hazard': ['heat', 'sun', 'hot', 'temperature'],
        'Drain Blockage': ['drain', 'manhole', 'sewage', 'gutter']
    }
    
    category = "Other"
    flag = "NEEDS_REVIEW"
    matched_cat = None
    
    for cat, kws in category_keywords.items():
        for kw in kws:
            if kw in desc_lower:
                category = cat
                flag = ""
                matched_cat = kw
                break
        if not flag:
            break
            
    if category == "Other":
        reason = "The description lacks clear categorization details, so we classify as Other."
    else:
        reason = f"Classified as {category} because the description mentions '{matched_cat}'."
        if matched_sev:
            reason += f" Also marked Urgent due to keyword '{matched_sev}'."
            
    return {
        "complaint_id": row.get("complaint_id", ""),
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
    fieldnames = []
    
    with open(input_path, 'r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames) + ['category', 'priority', 'reason', 'flag']
        for i, row in enumerate(reader):
            try:
                res = classify_complaint(row)
                out_row = dict(row)
                out_row.update(res)
                results.append(out_row)
            except Exception as e:
                print(f"Error on row {i+1}: {e}")
                
    with open(output_path, 'w', encoding='utf-8', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
