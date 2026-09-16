"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import csv
import argparse
import os

# Allowed schema values
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

def classify_complaint(description):
    """
    Classifies a single citizen complaint into category, priority, reason, and flag.
    """
    if not description or not isinstance(description, str):
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Invalid description provided",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # Determine priority
    priority = "Standard"
    if any(keyword in desc_lower for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"

    # Determine category
    category = None
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower or "waterlogging" in desc_lower:
        category = "Flooding"
    elif "light" in desc_lower or "lamp" in desc_lower:
        category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "trash" in desc_lower:
        category = "Waste"
    elif "noise" in desc_lower or "loud" in desc_lower:
        category = "Noise"
    elif "road" in desc_lower or "asphalt" in desc_lower:
        category = "Road Damage"
    elif "heritage" in desc_lower or "monument" in desc_lower or "temple" in desc_lower:
        category = "Heritage Damage"
    elif "heat" in desc_lower or "hot" in desc_lower or "temperature" in desc_lower:
        category = "Heat Hazard"
    elif "drain" in desc_lower or "sewage" in desc_lower or "blockage" in desc_lower:
        category = "Drain Blockage"
    else:
        category = "Other"

    # Reason must cite specific words
    reason = f"Complaint mentions '{description.strip()}'"

    # Flag ambiguous cases
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_file, output_file):
    """
    Reads an input CSV of complaints, applies classify_complaint to each row, and writes results to output CSV.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} not found.")

    results = []
    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if "description" not in reader.fieldnames:
            raise ValueError("Input CSV must contain a 'description' column.")
        for row in reader:
            desc = row.get("description", "")
            classified = classify_complaint(desc)
            results.append(classified)

    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["category", "priority", "reason", "flag"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    batch_classify(args.input, args.output)

if __name__ == "__main__":
    main()
