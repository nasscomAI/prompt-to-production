"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

import os

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "crater"],
    "Flooding": ["flood", "flooding", "waterlogging", "submerged", "water"],
    "Streetlight": ["streetlight", "street light", "dark", "lamp", "lights out"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "litter", "debris"],
    "Noise": ["noise", "loud", "sound", "music", "party", "disturbing"],
    "Road Damage": ["road damage", "crack", "broken road", "surface", "cave in", "sinkhole"],
    "Heritage Damage": ["heritage", "monument", "historic", "ruins", "statue"],
    "Heat Hazard": ["heat", "heatwave", "temperature", "sun"],
    "Drain Blockage": ["drain", "blockage", "clogged", "sewer", "overflowing"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row safely.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = str(row.get("description", "")).lower()
    
    # Check severity
    priority = "Standard"
    severity_match = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            severity_match = kw
            break
            
    # Find category matches
    matches = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in desc:
                if cat not in matches:
                    matches[cat] = []
                matches[cat].append(kw)
                
    # Evaluate matches against rules
    category = "Other"
    flag = "NEEDS_REVIEW"
    reason = "The description lacks explicit keywords to determine a clear category."

    if len(matches) == 1:
        # Clear, unambiguous match
        category = list(matches.keys())[0]
        flag = ""
        kw_found = matches[category][0]
        if priority == "Urgent":
            reason = f"The description contains '{kw_found}' assigning category '{category}', and urgent keyword '{severity_match}'."
        else:
            reason = f"The description contains the text '{kw_found}' mapping to '{category}'."
    elif len(matches) > 1:
        # Ambiguous match
        category = "Other"
        flag = "NEEDS_REVIEW"
        cats = list(matches.keys())
        reason = f"Ambiguous complaint mentioning keywords for multiple categories: {', '.join(cats)}."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely skip bad rows and handle missing files.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return
        
    results = []
    fieldnames = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames:
            fieldnames = list(reader.fieldnames)
            
        for row in reader:
            try:
                classified = classify_complaint(row)
                merged = {**row, **classified}
                results.append(merged)
            except Exception as e:
                print(f"Warning: Processing failed for row. Skipping: {e}")
                
    # Append newly generated classification fields
    for field in ["category", "priority", "reason", "flag"]:
        if field not in fieldnames:
            fieldnames.append(field)
            
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        return True
    except PermissionError:
        print(f"Error: Permission denied to write '{output_path}'.")
        print("Please ensure the file is not currently open in another program (like Excel or your IDE) and try again.")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    if batch_classify(args.input, args.output):
        print(f"Done. Results written to {args.output}")
