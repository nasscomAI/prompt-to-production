import argparse
import csv
import json
import os

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint based on RICE rules in agents.md.
    Strictly follows allowed categories and severity keywords.
    """
    desc_lower = description.lower()
    
    # 1. Priority Enforcement: Urgent if severity keywords present
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    found_severity_kw = None
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            found_severity_kw = kw
            break
            
    # 2. Category Enforcement: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    categories_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging", "rain", "stranded"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["garbage", "trash", "waste", "bins", "animal", "smell"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["road surface", "cracked", "sinking", "footpath", "tiles"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "hot"],
        "Drain Blockage": ["drain", "manhole", "sewage"]
    }
    
    matched_categories = []
    for cat, keywords in categories_map.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(cat)
                break
    
    category = "Other"
    flag = ""
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        # Handle ambiguity: set to 'Other' or first match and flag it
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        # No clear match
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 3. Reason Enforcement: One sentence, cite specific words
    # Find the actual word from description that triggered the classification
    cited_word = ""
    for kw in (severity_keywords + [k for sublist in categories_map.values() for k in sublist]):
        if kw in desc_lower:
            # Find the actual case-sensitive word from description
            start_idx = desc_lower.find(kw)
            cited_word = description[start_idx:start_idx+len(kw)]
            break
            
    if category != "Other":
        reason = f"The complaint is categorized as {category} because the description mentions '{cited_word or category.lower()}'."
    else:
        reason = "The complaint was flagged as Other because no specific category keywords were clearly identified."

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
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
            
            for row in reader:
                # Apply classify_complaint logic
                classification = classify_complaint(row.get('description', ''))
                row.update(classification)
                results.append(row)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Successfully processed {len(results)} rows.")
            
    except Exception as e:
        print(f"An error occurred during batch processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
