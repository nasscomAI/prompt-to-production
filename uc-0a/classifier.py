import csv
import argparse
import re
import os

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(description):
    desc_lower = description.lower()
    
    # 1. Category Assignment (Taxonomy drift & Hallucinated avoidance)
    category: str = "Other"
    flag: str = ""
    if "pothole" in desc_lower: category = "Pothole"
    elif "drain" in desc_lower and "block" in desc_lower: category = "Drain Blockage"
    elif "drain" in desc_lower: category = "Drain Blockage"
    elif "light" in desc_lower: category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower: category = "Waste"
    elif "noise" in desc_lower or "loud" in desc_lower: category = "Noise"
    elif "road" in desc_lower and "damage" in desc_lower: category = "Road Damage"
    elif "heritage" in desc_lower: category = "Heritage Damage"
    elif "water log" in desc_lower or "rain" in desc_lower: category = "Flooding"
    elif "heat" in desc_lower: category = "Heat Hazard"
    elif "ditch" in desc_lower: category = "Road Damage"
    else:
        # False confidence on ambiguity
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    if "stray dog" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Priority Assignment (Severity blindness fix)
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in desc_lower:
            priority = "Urgent"
            break
            
    # 3. Reason Extraction (Missing justification fix)
    reason_words = []
    for word in desc_lower.split():
        clean_word = re.sub(r'[^a-zA-Z]', '', word)
        if clean_word and (clean_word in SEVERITY_KEYWORDS or clean_word in str(category).lower()):
            reason_words.append(clean_word)
    
    if reason_words:
        reason = f"Classified because the description explicitly mentions '{reason_words[0]}'."
    elif priority == "Urgent":
        reason = "Classified as Urgent due to severity implications in the context."
    else:
        reason = f"Matches general pattern for {category}."
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_csv, output_csv):
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    
    with open(input_csv, 'r', encoding='utf-8') as fin, \
         open(output_csv, 'w', encoding='utf-8', newline='') as fout:
        reader = csv.DictReader(fin)
        _fn = reader.fieldnames
        base_fields = _fn if _fn is not None else ['id', 'description']
        fieldnames = [str(f) for f in base_fields] + ['category', 'priority', 'reason', 'flag']
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            row.pop(None, None)
            desc = row.get('description') or ""
            res = classify_complaint(desc)
            row.update(res)
            writer.writerow(row)
            print(f"Processed: {row['id']} -> {res['category']} ({res['priority']})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
