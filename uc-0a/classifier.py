"""
UC-0A — Complaint Classifier
Implementation based on RICE -> agents.md -> skills.md.
"""
import argparse
import csv
import re

# Enforced Categorization Taxonomy
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Keywords that exactly map to taxonomies
CATEGORY_MAPPING = {
    "Pothole": [r'pothole'],
    "Flooding": [r'flood'],
    "Streetlight": [r'streetlight', r'light', r'dark'],
    "Waste": [r'garbage', r'waste', r'animal'],
    "Noise": [r'music', r'noise', r'loud'],
    "Road Damage": [r'road surface', r'crack', r'broken', r'footpath', r'sinking'],
    "Heritage Damage": [r'heritage'],
    "Heat Hazard": [r'heat'],
    "Drain Blockage": [r'drain', r'blocked', r'manhole']
}

# The triggers required for 'Urgent' priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()
    
    assigned_category = "Other"
    reason_word = None
    
    # 1. Enforce Taxonomy Classification
    for cat, patterns in CATEGORY_MAPPING.items():
        for pat in patterns:
            # We look for the keyword in the description text
            match = re.search(r'\b' + pat + r'\w*\b', desc_lower, re.IGNORECASE)
            if match:
                assigned_category = cat
                # Extract the literal word found directly from the text for citation
                start, end = match.span()
                reason_word = desc[start:end]
                break
        if assigned_category != "Other":
            break
            
    # 2. Enforce Severity Blindness Prevention
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        severity_match = re.search(r'\b' + word + r'\w*\b', desc_lower, re.IGNORECASE)
        if severity_match:
            priority = "Urgent"
            # If we don't already have a reason word from the category, use the severity keyword
            if not reason_word:
                start, end = severity_match.span()
                reason_word = desc[start:end]
            break
            
    # 3. Enforce False Confidence on Ambiguity
    flag = "NEEDS_REVIEW" if assigned_category == "Other" else ""
    
    # 4. Enforce Missing Justification Rule (One-sentence reason citing specific words)
    if reason_word:
        reason = f"The classification is based on the specific word '{reason_word}' extracted from the description."
    else:
        reason = "The description text was too ambiguous to extract clear categorization triggers."
        
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": assigned_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely flags nulls and does not crash on bad rows.
    """
    results = []
    
    # Read phase
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for raw_row in reader:
                try:
                    res_row = classify_complaint(raw_row)
                    results.append(res_row)
                except Exception as row_e:
                    # Do not crash on bad rows, produce output
                    print(f"Error classifying row {raw_row.get('complaint_id', 'UNKNOWN')}: {row_e}")
                    results.append({
                        "complaint_id": raw_row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing crash: {str(row_e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read input file {input_path}. Error: {e}")
        return
        
    # Write phase
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as write_e:
        print(f"Failed to write results to {output_path}. Error: {write_e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
