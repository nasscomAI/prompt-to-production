import csv
import argparse
import os

# Allowed values from the UC-0A schema
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Keywords that trigger "Urgent" priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description):
    desc_lower = description.lower()
    category = "Other"
    priority = "Standard"
    flag = ""

    # Simple Keyword Mapping for Categories
    if "pothole" in desc_lower: category = "Pothole"
    elif "flood" in desc_lower: category = "Flooding"
    elif "light" in desc_lower: category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower: category = "Waste"
    elif "noise" in desc_lower: category = "Noise"
    elif "road" in desc_lower: category = "Road Damage"
    elif "heritage" in desc_lower: category = "Heritage Damage"
    elif "heat" in desc_lower: category = "Heat Hazard"
    elif "drain" in desc_lower: category = "Drain Blockage"

    # Severity Enforcement
    found_keywords = [word for word in SEVERITY_KEYWORDS if word in desc_lower]
    if found_keywords:
        priority = "Urgent"
        reason = f"Urgent: '{found_keywords[0]}' mentioned in description."
    else:
        reason = f"Classified as {category} based on keywords."

    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag

def batch_classify(input_path, output_path):
    if not os.path.exists(input_path):
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat, prio, reas, flg = classify_complaint(row.get('description', ''))
            row.update({'category': cat, 'priority': prio, 'reason': reas, 'flag': flg})
            results.append(row)

    if results:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
