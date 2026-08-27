import csv
import argparse

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(text):
    t = text.lower()

    # Category detection
    if "pothole" in t:
        category = "Pothole"
    elif "flood" in t or "water" in t:
        category = "Flooding"
    elif "light" in t:
        category = "Streetlight"
    elif "garbage" in t or "waste" in t:
        category = "Waste"
    elif "noise" in t or "drilling" in t:
        category = "Noise"
    elif "road damage" in t:
        category = "Road Damage"
    elif "heritage" in t:
        category = "Heritage Damage"
    elif "heat" in t:
        category = "Heat Hazard"
    elif "drain" in t:
        category = "Drain Blockage"
    else:
        category = "Other"

    # Priority detection
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in t:
            priority = "Urgent"

    # Reason field
    reason = f"Detected keywords in complaint: {text[:50]}"

    # Ambiguity flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    with open(input_file, newline="") as infile, open(output_file, "w", newline="") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            text = row["description"]

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

    print("Classification complete.")
