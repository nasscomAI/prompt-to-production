"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Configuration from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAPPING = {
    "Pothole": ["pothole", "hole", "crater"],
    "Flooding": ["flood", "waterlogging", "rain water"],
    "Streetlight": ["streetlight", "lamp", "dark", "street light"],
    "Waste": ["garbage", "trash", "waste", "rubbish", "dump"],
    "Noise": ["noise", "loud", "sound", "music", "cracker"],
    "Road Damage": ["road crack", "pavement", "surface", "asphalt"],
    "Heritage Damage": ["heritage", "statue", "monument", "historic"],
    "Heat Hazard": ["heat", "hot", "sun", "shade", "dehydration"],
    "Drain Blockage": ["drain", "blocked", "clogged", "sewage", "gutter"]
}

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint description.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc_lower = description.lower()
    
    # 1. Determine Category
    category = "Other"
    reason_word = ""
    
    for cat, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                reason_word = kw
                break
        if category != "Other":
            break
            
    # 2. Determine Priority
    priority = "Standard"
    urgent_found = []
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            urgent_found.append(kw)
    
    # 3. Handle Ambiguity
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "No specific category keywords found in description."
    else:
        reason_parts = [f"Contains keyword '{reason_word}'."]
        if priority == "Urgent":
            reason_parts.append(f"Severity keywords found: {', '.join(urgent_found)}.")
        reason = " ".join(reason_parts)

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    fieldnames = []

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            # Ensure we have a description column. 
            # We check common names if 'description' isn't exact.
            desc_col = None
            for col in fieldnames:
                if col.lower() in ['description', 'complaint', 'text']:
                    desc_col = col
                    break
            
            if not desc_col:
                print(f"Error: Could not find description column in {input_path}")
                return

            for row in reader:
                classification = classify_complaint(row.get(desc_col, ""))
                row.update(classification)
                results.append(row)

    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Add new fields to fieldnames if they aren't already there
    new_fields = ["category", "priority", "reason", "flag"]
    for field in new_fields:
        if field not in fieldnames:
            fieldnames.append(field)

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
