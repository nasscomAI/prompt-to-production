import argparse
import csv

def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description_raw = row.get("description") or ""
    description = description_raw.lower()

    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    matches = []

    if "pothole" in description:
        matches.append(("Pothole", "pothole"))

    if "flood" in description or "waterlogging" in description:
        matches.append(("Flooding", "flood"))

    if "streetlight" in description or ("light" in description and "street" in description):
        matches.append(("Streetlight", "streetlight"))

    if "garbage" in description or "waste" in description:
        matches.append(("Waste", "garbage"))

    if "noise" in description or "music" in description or "loud" in description:
        matches.append(("Noise", "noise"))

    if "road" in description or "tiles" in description or "footpath" in description:
        if "damage" in description or "broken" in description:
            matches.append(("Road Damage", "broken road"))

    if "drain" in description or "sewer" in description or "manhole" in description:
        matches.append(("Drain Blockage", "drain"))

    if len(matches) == 1:
        category, keyword = matches[0]
        flag = ""
    else:
        category = "Other"
        keyword = "unclear"
        flag = "NEEDS_REVIEW"

    severity_keywords = [
        "injury", "child", "school", "hospital",
        "ambulance", "fire", "hazard", "fell", "collapse"
    ]

    if any(word in description for word in severity_keywords):
        priority = "Urgent"
    else:
        priority = "Standard"

    reason = f"Detected '{keyword}' in description"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    print("Running classifier...")

    with open(input_path, newline='', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            result = classify_complaint(row)
            writer.writerow(result)

    print(f"Done. File saved as: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)