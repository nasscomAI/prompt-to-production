import os
import csv
import argparse

# 1. Allowed categories schema mapping (Deterministic matching)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# 2. Strict severity keywords
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(description):
    desc_lower = description.lower()
    
    # Base heuristic classification rules to guarantee exact strings
    category = "Other"
    if "pothole" in desc_lower or "crater" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower or "waterlogging" in desc_lower or "submerged" in desc_lower:
        category = "Flooding"
    elif "light" in desc_lower or "dark" in desc_lower or "lamp" in desc_lower:
        category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "trash" in desc_lower or "dump" in desc_lower:
        category = "Waste"
    elif "noise" in desc_lower or "loud" in desc_lower or "sound" in desc_lower or "speaker" in desc_lower:
        category = "Noise"
    elif "road" in desc_lower or "tarmac" in desc_lower or "asphalt" in desc_lower:
        category = "Road Damage"
    elif "heritage" in desc_lower or "monument" in desc_lower or "ancient" in desc_lower:
        category = "Heritage Damage"
    elif "heat" in desc_lower or "temperature" in desc_lower or "sunstroke" in desc_lower:
        category = "Heat Hazard"
    elif "drain" in desc_lower or "sewage" in desc_lower or "gutter" in desc_lower:
        category = "Drain Blockage"

    # Enforce priority rule safely
    priority = "Standard"
    matched_keyword = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            matched_keyword = kw
            break
            
    # Formulate contextual reasons
    if priority == "Urgent":
        reason = f"Flagged Urgent due to safety keyword '{matched_keyword}' in description."
    else:
        reason = f"Classified as {category} based on systemic contextual markers in complaint."

    # Ambiguity check flag
    flag = ""
    if category == "Other" or len(description.strip()) < 15:
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag

def batch_classify(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        # Keep original columns, but inject/overwrite expected targets
        if 'category' not in fieldnames: fieldnames.append('category')
        if 'priority' not in fieldnames: fieldnames.append('priority')
        if 'reason' not in fieldnames: fieldnames.append('reason')
        if 'flag' not in fieldnames: fieldnames.append('flag')

        rows = []
        for row in reader:
            # Dynamically handle whatever column naming convention is in the text
            desc = row.get('description', row.get('complaint', row.get('text', '')))
            
            cat, prio, reas, flg = classify_complaint(desc)
            row['category'] = cat
            row['priority'] = prio
            row['reason'] = reas
            row['flag'] = flg
            rows.append(row)

    with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Success! Output generated at: {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)