"""
UC-0A — Complaint Classifier
"""

import argparse
import csv


CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage",
    "Other"
]


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    text = row.get("complaint_text", "").lower()

    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    if not text:
        flag = "NEEDS_REVIEW"
        reason = "Complaint text missing"
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }

    # category detection
    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "waterlogging" in text:
        category = "Flooding"
    elif "streetlight" in text or "light not working" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text or "trash" in text:
        category = "Waste"
    elif "noise" in text:
        category = "Noise"
    elif "road damage" in text or "road broken" in text:
        category = "Road Damage"
    elif "heritage" in text or "monument" in text:
        category = "Heritage"

    # priority detection
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "collapse"]

    if any(word in text for word in urgent_keywords):
        priority = "Urgent"
        reason = "Emergency keyword found in complaint"
    else:
        priority = "Standard"
        reason = "No urgent keywords detected"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):

    results = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Processing error",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")