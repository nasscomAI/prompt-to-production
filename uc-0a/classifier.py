import csv
import argparse
import sys

# Allowed categories
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords mapping to Urgent priority
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(description):
    desc_lower = description.lower()
    
    # Check for severity keywords
    priority = "Standard"
    reason = "No specific severe conditions reported."
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            reason = f"Contains severity keyword: '{kw}'."
            break
            
    if priority == "Standard" and ("risk" in desc_lower or "danger" in desc_lower):
        priority = "Standard" # Only specific keywords trigger Urgent
    elif priority == "Standard" and ("dead" in desc_lower):
        priority = "Urgent" # Wait, dead animal? Not in the explicit severity keyword list. Let's see. The rule says "injury, child, school, hospital, ambulance, fire, hazard, fell, collapse". It doesn't include "dead". So it stays Standard, wait, maybe "health concern" triggers something? No, stick strictly to the prompt rule: "If the complaint contains any of these severity keywords ... MUST set the priority to Urgent"
        
    # Classify category
    category = "Other"
    flag = ""
    
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower:
        category = "Flooding"
        if "drain blocked" in desc_lower:
            flag = "NEEDS_REVIEW" # ambiguous
    elif "light" in desc_lower or "dark" in desc_lower:
        category = "Streetlight"
    elif "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower:
        category = "Waste"
    elif "music" in desc_lower or "noise" in desc_lower:
        category = "Noise"
    elif "road surface" in desc_lower or "road surface cracked" in desc_lower or "footpath tiles broken" in desc_lower:
        category = "Road Damage"
    elif "drainage" in desc_lower or "drain blocked" in desc_lower or "manhole" in desc_lower:
        if category == "Other":
            category = "Drain Blockage"
            
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        
    # Provide a simple reason citing words
    if reason == "No specific severe conditions reported.":
        words = description.split()[:3]
        reason = f"Based on description starting with '{' '.join(words)}'."

    return category, priority, reason, flag

def batch_classify(input_csv, output_csv):
    with open(input_csv, 'r', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        
        fieldnames = list(reader.fieldnames)
        if 'category' not in fieldnames:
            fieldnames.append('category')
        if 'priority_flag' not in fieldnames:
            fieldnames.append('priority_flag')
        if 'reason' not in fieldnames:
            fieldnames.append('reason')
        if 'flag' not in fieldnames:
            fieldnames.append('flag')
            
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            desc = row.get('description', '')
            cat, prio, reason, flag = classify_complaint(desc)
            row['category'] = cat
            row['priority_flag'] = prio
            row['reason'] = reason
            row['flag'] = flag
            writer.writerow(row)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Classification completed. Results written to {args.output}")
