"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(text):
    text_lower = text.lower()
    category = "Other"
    priority = "Standard"
    flag = ""

    if "pothole" in text_lower:
        category = "Pothole"
    elif "flood" in text_lower or "water" in text_lower:
        category = "Flooding"
    elif "light" in text_lower:
        category = "Streetlight"
    elif "garbage" in text_lower or "waste" in text_lower:
        category = "Waste"
    elif "noise" in text_lower:
        category = "Noise"
    elif "road" in text_lower:
        category = "Road Damage"
    elif "drain" in text_lower:
        category = "Drain Blockage"

    for word in URGENT_KEYWORDS:
        if word in text_lower:
            priority = "Urgent"
            break

    reason = f"Based on keywords in complaint: {text[:50]}"

    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        with open(output_file, "w", newline="", encoding="utf-8") as outfile:
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()

            for row in reader:
                text = row.get("complaint", "")
                category, priority, reason, flag = classify_complaint(text)

                row["category"] = category
                row["priority"] = priority
                row["reason"] = reason
                row["flag"] = flag

                writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print("✅ Classification completed!")


if __name__ == "__main__":
    main()