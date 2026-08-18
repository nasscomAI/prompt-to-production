import argparse
import csv
import os

# Schema definitions from README.md and agents.md
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAPPING = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "streetlight": "Streetlight",
    "light": "Streetlight",
    "waste": "Waste",
    "garbage": "Waste",
    "trash": "Waste",
    "noise": "Noise",
    "drilling": "Noise",
    "road damage": "Road Damage",
    "crack": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage",
    "sewage": "Drain Blockage"
}

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint based on description.
    Enforces RICE rules.
    """
    description_lower = description.lower()
    
    # Priority classification
    priority = "Standard"
    for kw in URGENT_KEYWORDS:
        if kw in description_lower:
            priority = "Urgent"
            break
            
    # Category classification
    category = "Other"
    found_keywords = []
    for kw, cat in CATEGORY_MAPPING.items():
        if kw in description_lower:
            category = cat
            found_keywords.append(kw)
            
    # Ambiguity check
    flag = ""
    # if ambiguous (multiple categories or none)
    unique_cats = set([CATEGORY_MAPPING[kw] for kw in CATEGORY_MAPPING if kw in description_lower])
    if len(unique_cats) > 1 or category == "Other":
        flag = "NEEDS_REVIEW"
        if len(unique_cats) == 0:
            category = "Other"
        
    # Reason field (citing words)
    if found_keywords:
        reason = f"Citing keywords: {', '.join(found_keywords)}"
    else:
        reason = "No specific category keywords found."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Process CSV and write results.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            rows = []
            for row in reader:
                desc = row.get("description", "")
                classification = classify_complaint(desc)
                row.update(classification)
                rows.append(row)
                
        with open(output_path, 'w', encoding='utf-8', newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
    except Exception as e:
        print(f"Error during processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    print(f"Processing {args.input}...")
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
