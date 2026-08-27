"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    # 1. Category Detection
    category = "Other"
    ambiguous = False
    
    # Exact category allowed values: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    if "heritage" in desc:
        category = "Heritage Damage"
        if "light" in desc:
            ambiguous = True # Heritage vs Streetlight
    elif "pothole" in desc:
        category = "Pothole"
    elif "drain" in desc or "manhole" in desc:
        category = "Drain Blockage"
        if "manhole" in desc:
            ambiguous = True # Manhole missing could be road damage or drain
    elif "flood" in desc:
        category = "Flooding"
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
    elif "garbage" in desc or "waste" in desc or "animal" in desc:
        category = "Waste"
    elif "music" in desc or "noise" in desc:
        category = "Noise"
    elif "road" in desc or "footpath" in desc:
        category = "Road Damage"
    elif "heat" in desc:
        category = "Heat Hazard"
        
    if ambiguous:
        flag = "NEEDS_REVIEW"
        category = "Other"
    else:
        flag = ""

    # 2. Priority Detection
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    found_keywords = []
    
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            found_keywords.append(kw)
            
    # low priority heuristic if 'days_open' is small and no severe words? 
    # Or just default Standard
    
    # 3. Reason Extraction
    if priority == "Urgent":
        reason = f"The description contains severity keywords: {', '.join(found_keywords)}."
    elif category != "Other":
        reason = f"The description mentions keywords that map it to {category}."
    else:
        reason = "The description text is ambiguous or unclassifiable."
        if not flag:
            flag = "NEEDS_REVIEW"
            
    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f_in, \
             open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            
            reader = csv.DictReader(f_in)
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for row in reader:
                try:
                    if not row.get('description'):
                        # Handle effectively null rows safely
                        writer.writerow({
                            'complaint_id': row.get('complaint_id', ''),
                            'category': 'Other',
                            'priority': 'Low',
                            'reason': 'No description provided.',
                            'flag': 'NEEDS_REVIEW'
                        })
                        continue
                    
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception as e:
                    # Don't crash on bad rows
                    print(f"Warning: Failed to process row {row.get('complaint_id', 'UNKNOWN')}: {e}", file=sys.stderr)
                    
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
