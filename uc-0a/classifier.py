"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

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
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()

    category = "Other"
    priority = "Standard"
    flag = ""

    # Category detection rules
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description:
        category = "Flooding"
    elif "streetlight" in description or "light" in description:
        category = "Streetlight"
    elif "garbage" in description or "waste" in description:
        category = "Waste"
    elif "noise" in description:
        category = "Noise"
    elif "road damage" in description or "broken road" in description:
        category = "Road Damage"
    elif "heritage" in description:
        category = "Heritage Damage"
    elif "heat" in description:
        category = "Heat Hazard"
    elif "drain" in description or "blockage" in description:
        category = "Drain Blockage"
    else:
        flag = "NEEDS_REVIEW"

    # Priority detection
    for word in SEVERITY_KEYWORDS:
        if word in description:
            priority = "Urgent"
            break

    # Reason generation
    reason = f'Based on keywords found in description: "{description[:50]}"'

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Failed to classify complaint",
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