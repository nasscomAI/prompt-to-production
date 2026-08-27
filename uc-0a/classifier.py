"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    
    category = "Other"
    flag = "NEEDS_REVIEW"
    matched_word = ""
    
    # Categorization heuristics
    if 'pothole' in description:
        category = "Pothole"
        matched_word = "pothole"
    elif 'flood' in description or 'waterlogging' in description:
        category = "Flooding"
        matched_word = "flood" if 'flood' in description else "waterlogging"
    elif 'streetlight' in description or 'lights out' in description:
        category = "Streetlight"
        matched_word = "streetlight" if 'streetlight' in description else "lights out"
    elif 'waste' in description or 'garbage' in description or 'dump' in description or 'dead animal' in description:
        category = "Waste"
        if 'waste' in description: matched_word = 'waste'
        elif 'garbage' in description: matched_word = 'garbage'
        elif 'dump' in description: matched_word = 'dump'
        else: matched_word = 'dead animal'
    elif 'noise' in description or 'music' in description:
        category = "Noise"
        matched_word = "noise" if 'noise' in description else "music"
    elif 'road surface' in description or 'crack' in description or 'manhole' in description or 'broken' in description:
        category = "Road Damage"
        if 'crack' in description: matched_word = 'crack'
        elif 'manhole' in description: matched_word = 'manhole'
        elif 'broken' in description: matched_word = 'broken'
        else: matched_word = 'road surface'
    elif 'drain' in description or 'sewage' in description:
        category = "Drain Blockage"
        matched_word = "drain" if 'drain' in description else "sewage"
    elif 'heritage' in description:
        category = "Heritage Damage"
        matched_word = "heritage"
    elif 'heat' in description:
        category = "Heat Hazard"
        matched_word = "heat"
        
    if category != "Other":
        flag = ""
        reason = f"The description mentions '{matched_word}'."
    else:
        reason = "The description is genuinely ambiguous and does not match known categories."

    # Priority determination
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', description):
            priority = "Urgent"
            reason += f" Priority escalated to Urgent due to severity keyword '{kw}'."
            break
            
    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason.strip(),
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Skipping malformed row due to error: {e}")
    except FileNotFoundError:
        print(f"Error: The file {input_path} could not be found.")
        return
        
    # As per skills.md: Nomenclature has to be like results_pune.csv Where the name of the city will be taken from the input file name.
    # However, output_path is provided by the arg parser. We'll write to output_path.
    
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
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
