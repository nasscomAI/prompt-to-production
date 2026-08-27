import csv
import argparse

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
]


def classify_complaint(description):
    desc = description.lower()

    # ----- Category classification -----
    if "pothole" in desc:
        category = "Pothole"
    elif "flood" in desc:
        category = "Flooding"
    elif "streetlight" in desc or "light" in desc:
        category = "Streetlight"
    elif "garbage" in desc or "waste" in desc or "animal" in desc:
        category = "Waste"
    elif "music" in desc or "noise" in desc:
        category = "Noise"
    elif "crack" in desc or "road" in desc or "manhole" in desc or "tile" in desc:
        category = "Road Damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "drain" in desc:
        category = "Drain Blockage"
    else:
        category = "Other"

    # ----- Priority detection -----
    priority = "Standard"

    for word in SEVERITY_KEYWORDS:
        if word in desc:
            priority = "Urgent"
            break

    # ----- Reason field -----
    reason = f"Classification based on keywords in description: {description}"

    # ----- Flag -----
    flag = ""

    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):

    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with open(output_file, "w", newline="", encoding="utf-8") as f:

        fieldnames = ["category", "priority", "reason", "flag"]

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for row in rows:
            category, priority, reason, flag = classify_complaint(row["description"])

            writer.writerow({
                "category": category,
                "priority": priority,
                "reason": reason,
                "flag": flag
            })


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
