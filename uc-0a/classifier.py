"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Predefined taxonomy based on agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords for Urgent priority
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Keyword-to-Category mapping to prevent taxonomy drift
CATEGORY_MAPPING = {
    "Pothole": ["pothole", "cavity", "pit"],
    "Flooding": ["flood", "water", "waterlogging", "inundation"],
    "Streetlight": ["light", "dark", "streetlamp", "lamp"],
    "Waste": ["garbage", "trash", "waste", "rubbish", "dump"],
    "Noise": ["noise", "loud", "sound", "speaker", "nuisance"],
    "Road Damage": ["road", "crack", "asphalt", "broken"],
    "Heritage Damage": ["heritage", "monument", "statue", "temple", "old building"],
    "Heat Hazard": ["heat", "sun", "shelter", "temperature", "hot"],
    "Drain Blockage": ["drain", "sewage", "gutter", "block"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using the R.I.C.E. enforcement rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    # Initial defaults
    category = "Other"
    priority = "Standard"
    reason = "No justification provided."
    flag = ""

    # 1. Category Classification (Preventing Taxonomy Drift)
    matched_categories = []
    for cat, keywords in CATEGORY_MAPPING.items():
        if any(kw in description for kw in keywords):
            matched_categories.append(cat)
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        reason = f"Identified as {category} due to mentions of {', '.join([k for k in CATEGORY_MAPPING[category] if k in description])}."
    elif len(matched_categories) > 1:
        category = matched_categories[0] # Pick first but flag for review
        flag = "NEEDS_REVIEW"
        reason = f"Multiple categories matched ({', '.join(matched_categories)}). Defaulted to {category}."
    else:
        # Ambiguity check
        flag = "NEEDS_REVIEW"
        category = "Other"
        reason = "The description does not clearly match any specific category."

    # 2. Priority Enforcement (Severity Blindness Prevention)
    found_urgent_keywords = [kw for kw in URGENT_KEYWORDS if kw in description]
    if found_urgent_keywords:
        priority = "Urgent"
        reason += f" Priority set to Urgent due to keywords: {', '.join(found_urgent_keywords)}."
    elif "low" in description or "minor" in description:
        priority = "Low"

    # 3. Final Result Formatting
    return {
        "complaint_id": complaint_id,
        "description": row.get("description", ""),
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                classified_row = classify_complaint(row)
                results.append(classified_row)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    if not results:
        print("No data processed.")
        return

    # Prepare output fieldnames
    output_fieldnames = ["complaint_id", "description", "category", "priority", "reason", "flag"]
    
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
