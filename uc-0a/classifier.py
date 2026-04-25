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
    description = row.get('description', '')
    if not description:
        description = ""
    desc_lower = description.lower()
    
    # 1. Determine Priority based on strict severity keywords
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    for kw in urgent_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            break
            
    # 2. Determine Category based on keywords
    categories = {
        "Pothole": ["pothole"],
        "Flooding": ["flooded", "floods", "flood"],
        "Drain Blockage": ["drain blocked", "drainage"],
        "Streetlight": ["streetlight", "lights out"],
        "Waste": ["garbage", "waste", "dead animal"],
        "Noise": ["music", "noise"],
        "Road Damage": ["surface cracked", "manhole", "footpath", "road surface"],
        "Heritage Damage": ["heritage damage"],
        "Heat Hazard": ["heat hazard", "heatstroke"]
    }
    
    matched_category = "Other"
    matched_keyword = ""
    flag = ""
    
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_category = cat
                matched_keyword = kw
                break
        if matched_category != "Other":
            break
            
    # 3. Handle Ambiguity
    if matched_category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Could not confidently determine category from description, marking for review."
    else:
        reason = f"Classified as {matched_category} because description mentions '{matched_keyword}'."
        
    return {
        "complaint_id": row.get('complaint_id', ''),
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Handle nulls
                    if not row.get('description') or not row.get('description').strip():
                        results.append({
                            'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                            'category': 'Other',
                            'priority': 'Standard',
                            'reason': 'Description is null or empty',
                            'flag': 'NEEDS_REVIEW'
                        })
                        continue
                    
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    results.append({
                        'complaint_id': row.get('complaint_id', 'ERROR'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': f'Error processing row: {e}',
                        'flag': 'NEEDS_REVIEW'
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except IOError as e:
        print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
