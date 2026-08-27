# classifier.py - UC-0A Complaint Classifier
import csv
import argparse

# Predefined schema
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row):
    """Classify a single complaint row."""
    description = row["description"].lower()
    category = "Other"
    priority = "Standard"
    flag = ""
    reason = ""
    
    # Determine category
    if "pothole" in description:
        category = "Pothole"
        reason = "Description mentions 'pothole'."
    elif "flood" in description or "water" in description:
        category = "Flooding"
        reason = "Description mentions 'flood' or 'water'."
    elif "streetlight" in description or "light" in description:
        category = "Streetlight"
        reason = "Description mentions 'streetlight' or 'light'."
    elif "waste" in description or "garbage" in description or "trash" in description:
        category = "Waste"
        reason = "Description mentions 'waste', 'garbage', or 'trash'."
    elif "noise" in description:
        category = "Noise"
        reason = "Description mentions 'noise'."
    elif "road damage" in description or "damage" in description:
        category = "Road Damage"
        reason = "Description mentions 'road damage' or 'damage'."
    elif "heritage" in description:
        category = "Heritage Damage"
        reason = "Description mentions 'heritage'."
    elif "heat" in description or "temperature" in description:
        category = "Heat Hazard"
        reason = "Description mentions 'heat' or 'temperature'."
    elif "drain" in description or "block" in description:
        category = "Drain Blockage"
        reason = "Description mentions 'drain' or 'block'."
    else:
        flag = "NEEDS_REVIEW"
        reason = "Category could not be determined from the description."
    
    # Determine priority
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = "Urgent"
            reason += f" Priority set to Urgent due to keyword: '{keyword}'."
            break
    
    return {
        "complaint_id": row["complaint_id"],
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path, output_path):
    """Classify all complaints in the input CSV and write results to output CSV."""
    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    classified_rows = [classify_complaint(row) for row in rows]
    
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify civic complaints.")
    parser.add_argument("--input", required=True, help="Path to input CSV file.")
    parser.add_argument("--output", required=True, help="Path to output CSV file.")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)