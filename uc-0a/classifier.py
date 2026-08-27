import csv
import argparse

# Allowed categories
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

# Severity keywords for urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(text):
    text_lower = text.lower()

    # Determine category
    if "pothole" in text_lower:
        category = "Pothole"
    elif "flood" in text_lower:
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
    else:
        category = "Other"

    # Determine priority
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in text_lower:
            priority = "Urgent"
            break

    # Reason
    reason = f"Detected keywords in complaint: {text[:40]}"

    # Flag ambiguity
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    with open(input_file, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        rows = []

        for row in reader:
            description = row["description"]

            category, priority, reason, flag = classify_complaint(description)

            rows.append({
                "description": description,
                "category": category,
                "priority": priority,
                "reason": reason,
                "flag": flag
            })

    with open(output_file, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["description", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)