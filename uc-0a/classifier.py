import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_WORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description):
    text = description.lower()

    priority = "Urgent" if any(word in text for word in URGENT_WORDS) else "Standard"

    flag = ""

    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "waterlogging" in text:
        category = "Flooding"
    elif "streetlight" in text or "light" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text or "trash" in text:
        category = "Waste"
    elif "noise" in text or "loud" in text:
        category = "Noise"
    elif "road" in text or "broken" in text:
        category = "Road Damage"
    elif "heritage" in text or "monument" in text:
        category = "Heritage Damage"
    elif "heat" in text or "hot" in text:
        category = "Heat Hazard"
    elif "drain" in text or "sewage" in text:
        category = "Drain Blockage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    reason = f"Classified as {category} because complaint mentions: '{description[:80]}'."

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    with open(input_file, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = []

        for row in reader:
            description = row.get("description", "")
            complaint_id = row.get("complaint_id", "")

            category, priority, reason, flag = classify_complaint(description)

            rows.append({
                "complaint_id": complaint_id,
                "category": category,
                "priority": priority,
                "reason": reason,
                "flag": flag
            })

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)