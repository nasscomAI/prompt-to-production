"""
UC-0A — Complaint Classifier
"""
import argparse
import csv


def classify_complaint(row: dict) -> dict:
    text = (row.get("description") or "").lower()

    # Category detection (ONLY allowed values)
    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "water" in text:
        category = "Flooding"
    elif "light" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text:
        category = "Waste"
    elif "noise" in text:
        category = "Noise"
    elif "road" in text:
        category = "Road Damage"
    elif "drain" in text:
        category = "Drain Blockage"
    elif "heat" in text:
        category = "Heat Hazard"
    else:
        category = "Other"

    # Priority detection
    urgent_keywords = [
        "injury", "child", "school", "hospital",
        "ambulance", "fire", "hazard", "fell", "collapse"
    ]

    if any(word in text for word in urgent_keywords):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Reason (must reference description)
    reason = f"Detected keywords in description: {text[:60]}"

    # Flag ambiguous cases
    flag = ""
    if category == "Other" or text.strip() == "":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Error processing complaint",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
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