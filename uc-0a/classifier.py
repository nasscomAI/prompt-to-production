import csv
import argparse

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description):
    desc = description.lower()

    category = "Other"
    flag = ""

    if "pothole" in desc:
        category = "Pothole"
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
    elif "light" in desc:
        category = "Streetlight"
    elif "garbage" in desc or "waste" in desc:
        category = "Waste"
    elif "noise" in desc:
        category = "Noise"
    elif "road" in desc:
        category = "Road Damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "heat" in desc:
        category = "Heat Hazard"
    elif "drain" in desc:
        category = "Drain Blockage"

    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in desc:
            priority = "Urgent"
            break

    if category == "Other":
        flag = "NEEDS_REVIEW"

    reason = f"Based on complaint text: '{description[:50]}'"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                description = list(row.values())[0]

                result = classify_complaint(description)

                row.update(result)
                writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)