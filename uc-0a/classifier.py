import csv
import argparse

# Allowed categories
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(text):
    text_lower = text.lower()

    # Default values
    category = "Other"
    priority = "Standard"
    flag = ""
    reason = ""

    # Category detection
    if "pothole" in text_lower:
        category = "Pothole"
    elif "flood" in text_lower or "waterlogging" in text_lower:
        category = "Flooding"
    elif "light" in text_lower:
        category = "Streetlight"
    elif "garbage" in text_lower or "waste" in text_lower:
        category = "Waste"
    elif "noise" in text_lower:
        category = "Noise"
    elif "road" in text_lower:
        category = "Road Damage"
    elif "heritage" in text_lower:
        category = "Heritage Damage"
    elif "heat" in text_lower:
        category = "Heat Hazard"
    elif "drain" in text_lower:
        category = "Drain Blockage"

    # Priority detection
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text_lower:
            priority = "Urgent"
            break

    # Reason (must cite words)
    reason = f"Detected keywords in complaint: '{text[:50]}'"

    # Ambiguity check
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            text = row.get("complaint", "")

            category, priority, reason, flag = classify_complaint(text)

            row["category"] = category
            row["priority"] = priority
            row["reason"] = reason
            row["flag"] = flag

            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)