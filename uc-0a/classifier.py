import csv
import argparse

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

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogging"],
    "Streetlight": ["streetlight", "light"],
    "Waste": ["garbage", "waste", "trash"],
    "Noise": ["noise", "loud"],
    "Road Damage": ["road damage", "broken road"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat", "hot"],
    "Drain Blockage": ["drain", "sewage"]
}


def classify_complaint(description):
    text = description.lower()

    category = "Other"
    flag = ""

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                category = cat
                break

    matches = 0
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                matches += 1

    if matches > 1 or category == "Other":
        flag = "NEEDS_REVIEW"

    priority = "Standard"

    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            priority = "Urgent"
            break

    reason = f"Detected keywords from complaint: {description[:50]}"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_file, output_file):
    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    output_rows = []

    for row in rows:
        description = row.get("description", "")
        result = classify_complaint(description)

        row["category"] = result["category"]
        row["priority"] = result["priority"]
        row["reason"] = result["reason"]
        row["flag"] = result["flag"]

        output_rows.append(row)

    fieldnames = output_rows[0].keys()

    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Classification complete. Output saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)