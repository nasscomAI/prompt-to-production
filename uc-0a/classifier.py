import argparse
import csv
import os

# Classification Schema
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAP = {
    "pothole": "Pothole",
    "hole": "Pothole",
    "flood": "Flooding",
    "water": "Flooding",
    "light": "Streetlight",
    "dark": "Streetlight",
    "lamp": "Streetlight",
    "garbage": "Waste",
    "trash": "Waste",
    "waste": "Waste",
    "noise": "Noise",
    "loud": "Noise",
    "sound": "Noise",
    "road": "Road Damage",
    "heritage": "Heritage Damage",
    "monument": "Heritage Damage",
    "heat": "Heat Hazard",
    "hot": "Heat Hazard",
    "hazzard": "Heat Hazard",
    "drain": "Drain Blockage",
    "sewage": "Drain Blockage"
}

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint row based on the description.
    """
    if not description or not isinstance(description, str):
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or invalid.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    
    # Category detection
    category = "Other"
    matched_cats = []
    for keyword, cat in CATEGORY_MAP.items():
        if keyword in desc_lower:
            matched_cats.append(cat)
            
    if matched_cats:
        category = matched_cats[0]
            
    # Priority detection
    priority = "Standard"
    found_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if found_keywords:
        priority = "Urgent"
        reason = f"Urgent priority due to severity keywords: {', '.join(found_keywords)}."
    else:
        reason = f"Classified as {category} because of keywords in description."

    # One sentence reason as per README
    reason = reason.split('.')[0] + "."

    # Flagging
    flag = ""
    # If category is Other, or multiple categories matched, flag it.
    if category == "Other" or len(set(matched_cats)) > 1:
        flag = "NEEDS_REVIEW"

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
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            for row in reader:
                description = row.get("description", "")
                classification = classify_complaint(description)
                row.update(classification)
                results.append(row)
    except Exception as e:
        print(f"Error reading input: {e}")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
