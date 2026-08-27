"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md requirements.
"""
import argparse
import csv
import re
import json

# Constants defined by agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SAFETY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "rain", "water"],
    "Streetlight": ["streetlight", "light", "dark"],
    "Waste": ["garbage", "waste", "animal", "smell", "dumped"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["crack", "sink", "surface", "footpath", "tiles"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "hot"],
    "Drain Blockage": ["drain", "sewage", "manhole", "overflowing"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Input: dict containing 'complaint_id' and 'description'
    Returns: dict { complaint_id: { original_data + classification_fields } }
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Determine Category
    category = "Other"
    matched_keyword = None
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                category = cat
                matched_keyword = kw
                break
        if category != "Other":
            break
            
    # 2. Determine Priority
    priority = "Standard"
    safety_trigger = None
    for kw in SAFETY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            safety_trigger = kw
            break
            
    if priority == "Standard" and "urgent" in description:
        priority = "Urgent" # Minor heuristic improvement
    elif priority == "Standard" and ("low" in description or "minor" in description):
        priority = "Low"

    # 3. Generate Reason
    # Rule: Must cite specific words from description
    if safety_trigger:
        reason = f"Classified as Urgent due to the presence of safety-critical keyword: '{safety_trigger}'."
    elif matched_keyword:
        reason = f"Categorized as {category} based on description mentioning '{matched_keyword}'."
    else:
        reason = "Classified as Other because no specific taxonomy keywords were identified in the description."

    # 4. Set Flag
    flag = ""
    if category == "Other" or not description:
        flag = "NEEDS_REVIEW"

    # Assemble result
    result_fields = {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }
    
    # Merge with original row data as per intent
    full_data = {**row, **result_fields}
    
    return {complaint_id: full_data}


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and generate results.
    Returns the master dictionary and writes to CSV.
    """
    master_dict = {}
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            for row in reader:
                classification = classify_complaint(row)
                master_dict.update(classification)
                
        # Write to Output CSV
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for comp_id in master_dict:
                writer.writerow(master_dict[comp_id])
                
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    return master_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    results = batch_classify(args.input, args.output)
    
    # Optionally print a snippet of the dictionary to console for verification
    # print(json.dumps(dict(list(results.items())[:2]), indent=2))
    
    print(f"Done. {len(results)} rows processed. Results written to {args.output}")
