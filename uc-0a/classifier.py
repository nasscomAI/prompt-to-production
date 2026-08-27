import csv
import argparse

CATEGORIES = [
    "Pothole","Flooding","Streetlight","Waste","Noise",
    "Road Damage","Heritage Damage","Heat Hazard","Drain Blockage","Other"
]

SEVERITY_KEYWORDS = [
    "injury","child","school","hospital","ambulance",
    "fire","hazard","fell","collapse"
]


def classify_complaint(description):

    text = description.lower()
    category = "Other"

    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "waterlogging" in text:
        category = "Flooding"
    elif "streetlight" in text or "light not working" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text:
        category = "Waste"
    elif "noise" in text or "loud" in text:
        category = "Noise"
    elif "road broken" in text or "road damage" in text:
        category = "Road Damage"
    elif "drain" in text:
        category = "Drain Blockage"

    priority = "Standard"

    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"
            break

    reason = f"Detected keywords in complaint: {description[:40]}"

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):

    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = []

    for row in rows:

        description = row["description"]

        category, priority, reason, flag = classify_complaint(description)

        results.append({
            "description": description,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        })

    with open(output_file, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=["description","category","priority","reason","flag"]
        )

        writer.writeheader()
        writer.writerows(results)

    print("Classification complete.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)