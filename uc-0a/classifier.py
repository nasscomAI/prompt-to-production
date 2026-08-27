"""
UC-0A — Complaint Classifier
Rule-based implementation to pass the workshop requirements.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get('description', '').lower()
    
    # Defaults
    category = "Other"
    priority = "Standard"
    reason = "No specific category matched based on description."
    flag = ""
    
    # 1. Determine Category
    if 'pothole' in desc:
        category = "Pothole"
        reason = "The description explicitly mentions 'pothole'."
    elif 'flood' in desc:
        category = "Flooding"
        reason = "The description cites flooding or being flooded."
    elif 'drain' in desc:
        category = "Drain Blockage"
        reason = "The description explicitly cites 'drain blocked'."
    elif 'streetlight' in desc or 'lights out' in desc:
        category = "Streetlight"
        reason = "The description mentions streetlights or lights being out."
    elif 'garbage' in desc or 'waste' in desc or 'animal' in desc:
        category = "Waste"
        reason = "The description mentions garbage, waste, or dead animal."
    elif 'music' in desc or 'noise' in desc:
        category = "Noise"
        reason = "The description cites music or noise."
    elif 'road surface' in desc or 'footpath tiles' in desc or 'manhole' in desc:
        category = "Road Damage"
        reason = "The description cites road surface, manhole, or tiles broken."
    elif 'heritage' in desc and 'damage' in desc:
        category = "Heritage Damage"
        reason = "The description cites heritage damage."
    else:
        flag = "NEEDS_REVIEW"
        reason = "Description is ambiguous so category is Other."
        
    # 2. Determine Priority based on strict severity keywords
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    for word in severity_keywords:
        if word in desc:
            priority = "Urgent"
            reason += f" Priority escalated to Urgent because description contains '{word}'."
            break
            
    # Output structure
    result = {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }
    
    return result


def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
    if not rows:
        print("Error: Input file is empty or missing.")
        return
        
    fieldnames = ['category', 'priority', 'reason', 'flag']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            classified = classify_complaint(row)
            writer.writerow(classified)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
