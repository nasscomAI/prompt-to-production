import csv
import argparse

SEVERITY_KEYWORDS = [
    "injury","child","school","hospital","ambulance",
    "fire","hazard","fell","collapse"
]

CATEGORY_MAP = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "water": "Flooding",
    "streetlight": "Streetlight",
    "light": "Streetlight",
    "waste": "Waste",
    "garbage": "Waste",
    "noise": "Noise",
    "road": "Road Damage",
    "drain": "Drain Blockage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard"
}

def classify_complaint(description):

    text = description.lower()

    category = "Other"
    for key in CATEGORY_MAP:
        if key in text:
            category = CATEGORY_MAP[key]
            break

    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"
            break

    reason = f"Detected keywords in complaint: {description}"

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):

    with open(input_file, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        with open(output_file, "w", newline='', encoding="utf-8") as outfile:

            fieldnames = reader.fieldnames + [
                "category","priority","reason","flag"
            ]

            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:

                category, priority, reason, flag = classify_complaint(
                    row["description"]
                )

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