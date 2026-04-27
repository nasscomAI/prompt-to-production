
import csv
import argparse

# Exact category list from README
CATEGORY_KEYWORDS = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "waterlogged": "Flooding",
    "streetlight": "Streetlight",
    "garbage": "Waste",
    "waste": "Waste",
    "noise": "Noise",
    "road": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage"
}

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(description: str):
    text = description.lower()
    matches = []

    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in text:
            matches.append((keyword, category))

    # Category logic
    if len(matches) == 1:
        keyword, category = matches[0]
        reason = f"Detected keyword '{keyword}' in complaint text."
        flag = ""
    elif len(matches) == 0:
        category = "Other"
        reason = "No explicit category indicators found in complaint."
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        keywords = ", ".join(k for k, _ in matches)
        reason = f"Multiple possible category indicators found: {keywords}."
        flag = "NEEDS_REVIEW"

    # Priority logic
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"
            reason += f" Severity keyword '{word}' detected."
            break

    return category, priority, reason, flag


def batch_classify(input_file: str, output_file: str):
    with open(input_file, newline="", encoding="utf-8") as infile, \
         open(output_file, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            description = row.get("description", "").strip()

            if not description:
                row.update({
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Missing complaint description.",
                    "flag": "NEEDS_REVIEW"
                })
            else:
                category, priority, reason, flag = classify_complaint(description)
                row.update({
                    "category": category,
                    "priority": priority,
                    "reason": reason,
                    "flag": flag
                })

            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)
