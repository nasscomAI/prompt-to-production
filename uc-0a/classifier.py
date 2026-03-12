import csv
import argparse

SEVERITY_WORDS = ["injury","child","school","hospital","ambulance","fire","hazard","fell","collapse"]

CATEGORIES = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "water": "Flooding",
    "streetlight": "Streetlight",
    "light": "Streetlight",
    "garbage": "Waste",
    "waste": "Waste",
    "noise": "Noise",
    "loud": "Noise",
    "road": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage",
    "sewer": "Drain Blockage"
}

def classify_complaint(description):

    text = description.lower()

    category = "Other"
    flag = ""

    for key in CATEGORIES:
        if key in text:
            category = CATEGORIES[key]
            break

    if category == "Other":
        flag = "NEEDS_REVIEW"

    priority = "Standard"
    for word in SEVERITY_WORDS:
        if word in text:
            priority = "Urgent"

    reason = f"Classified due to keywords found in description: '{description[:40]}'"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):

    with open(input_file, newline='', encoding="utf-8") as infile, \
         open(output_file, "w", newline='', encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = reader.fieldnames + ["category","priority","reason","flag"]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:

            description = row["description"]

            category, priority, reason, flag = classify_complaint(description)

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
