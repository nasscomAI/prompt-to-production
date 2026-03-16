import csv
import argparse

severity_keywords = ["injury","child","school","hospital","ambulance","fire","hazard","fell","collapse"]

def classify_complaint(text):
    text_lower = text.lower()

    if "pothole" in text_lower:
        category = "Pothole"
    elif "flood" in text_lower or "water" in text_lower:
        category = "Flooding"
    elif "light" in text_lower:
        category = "Streetlight"
    elif "garbage" in text_lower or "trash" in text_lower or "waste" in text_lower:
        category = "Waste"
    elif "noise" in text_lower or "loud" in text_lower:
        category = "Noise"
    elif "road damage" in text_lower or "broken road" in text_lower:
        category = "Road Damage"
    elif "heritage" in text_lower:
        category = "Heritage Damage"
    elif "heat" in text_lower:
        category = "Heat Hazard"
    elif "drain" in text_lower:
        category = "Drain Blockage"
    else:
        category = "Other"

    priority = "Standard"
    for word in severity_keywords:
        if word in text_lower:
            priority = "Urgent"

    reason = f"Detected keywords in description: {text[:30]}"
    flag = ""

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    with open(input_file, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    with open(output_file, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = reader.fieldnames + ["category","priority","reason","flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in rows:
            category, priority, reason, flag = classify_complaint(row["description"])
            row["category"] = category
            row["priority"] = priority
            row["reason"] = reason
            row["flag"] = flag
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")

    args = parser.parse_args()

    batch_classify(args.input, args.output)