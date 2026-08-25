
import argparse
import csv

# Allowed categories (must match exactly)
CATEGORIES = [
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

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    text = description.lower()

    category = "Other"
    flag = ""

    # Category detection
    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "water logging" in text:
        category = "Flooding"
    elif "light" in text or "streetlight" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text or "trash" in text:
        category = "Waste"
    elif "noise" in text or "loud" in text:
        category = "Noise"
    elif "road" in text or "crack" in text or "broken road" in text:
        category = "Road Damage"
    elif "heritage" in text or "monument" in text:
        category = "Heritage Damage"
    elif "heat" in text:
        category = "Heat Hazard"
    elif "drain" in text or "sewer" in text:
        category = "Drain Blockage"

    # Priority detection
    priority = "Standard"
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            priority = "Urgent"
            break

    if category == "Other":
        flag = "NEEDS_REVIEW"

    reason = f"Detected words from complaint: '{description[:40]}'"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must not crash on bad rows.
    """

    results = []

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")