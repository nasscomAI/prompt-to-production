import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")

    # Default values
    category = "Other"
    priority = "Low"
    flag = ""
    reason = ""

    # Category detection (basic keyword matching)
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description:
        category = "Flooding"
    elif "light" in description:
        category = "Streetlight"
    elif "garbage" in description or "waste" in description:
        category = "Waste"
    elif "noise" in description:
        category = "Noise"
    elif "road damage" in description:
        category = "Road Damage"
    elif "drain" in description:
        category = "Drain Blockage"

    # Priority detection
    if any(word in description for word in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Reason
    reason = f"Detected keywords in description: {description[:50]}"

    # Ambiguity check
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, "r") as infile, open(output_path, "w", newline="") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                print(f"Error processing row: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")