import csv
import argparse
import os

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pit", "hole in road"],
    "Flooding": ["flood", "waterlogging", "water on road", "rain water"],
    "Streetlight": ["streetlight", "street light", "lamp", "dark", "no light"],
    "Waste": ["waste", "garbage", "trash", "dump", "smell", "stink"],
    "Noise": ["noise", "loud", "sound", "speaker", "disturb"],
    "Road Damage": ["road damage", "crack", "broken road", "tar"],
    "Heritage Damage": ["heritage", "monument", "statue", "old building"],
    "Heat Hazard": ["heat", "hot", "sunstroke", "dehydration"],
    "Drain Blockage": ["drain", "sewage", "gutter", "blockage", "overflow"],
}

def classify_complaint(description):
    desc_lower = description.lower()
    
    # Priority
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break
            
    # Category
    category = "Other"
    found_categories = []
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in desc_lower:
                found_categories.append(cat)
                break
    
    flag = ""
    if len(found_categories) == 1:
        category = found_categories[0]
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        if not desc_lower.strip():
            flag = "NEEDS_REVIEW"
            
    # Reason
    if category != "Other":
        reason = f"Classified as {category} because description mentions keywords related to {category.lower()}."
    elif flag == "NEEDS_REVIEW":
        reason = "Ambiguous description with multiple or no clear category matches."
    else:
        reason = "No specific category keywords found."
        
    # Citation (simulated)
    # Finding the first keyword that matched
    cited_word = ""
    if category in CATEGORY_KEYWORDS:
        for kw in CATEGORY_KEYWORDS[category]:
            if kw in desc_lower:
                cited_word = kw
                break
    
    if cited_word:
        reason = f"Description mentions '{cited_word}', indicating a {category.lower()} issue."
    elif priority == "Urgent":
        for kw in SEVERITY_KEYWORDS:
            if kw in desc_lower:
                reason = f"Urgent priority due to mention of '{kw}'."
                break

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return

    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        
        with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                description = row.get("description", "")
                result = classify_complaint(description)
                row.update(result)
                writer.writerow(row)
                
    print(f"Successfully processed {input_file} -> {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify citizen complaints.")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
