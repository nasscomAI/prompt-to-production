import csv
import argparse

# Allowed categories
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

# Severity keywords → Urgent
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(description):
    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description",
            "flag": "NEEDS_REVIEW"
        }
    
    desc = str(description).lower()

    category = "Other"
    flag = ""
    
    # Simple keyword-based classification
    if "pothole" in desc:
        category = "Pothole"
    elif "flood" in desc or "water logging" in desc:
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

    # Priority logic
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in desc:
            priority = "Urgent"
            break

    # Ambiguity check
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Reason (must reference text)
    desc_start = desc[:50]
    reason = f"Based on keywords in complaint: '{desc_start}'"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames or []) + ["category", "priority", "reason", "flag"]

        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    description = row.get("description", "") or row.get("complaint", "")
                    # Fallback to description index if present
                    if not description and len(row) > 5:
                        description = list(row.values())[5]
                        
                    result = classify_complaint(description)
                    row.update(result)
                except Exception as e:
                    # Do not crash on bad rows
                    row.update({
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error: {e}",
                        "flag": "ERROR"
                    })
                
                writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)