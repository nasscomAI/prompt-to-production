"""
UC-0A — Complaint Classifier
"""

import argparse
import csv

# Allowed categories
CATEGORIES = [
    "Pothole","Flooding","Streetlight","Waste","Noise",
    "Road Damage","Heritage Damage","Heat Hazard","Drain Blockage","Other"
]

# Severity keywords for Urgent
SEVERITY_KEYWORDS = [
    "injury","child","school","hospital","ambulance",
    "fire","hazard","fell","collapse"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with complaint_id, category, priority, reason, flag
    """

    text = row.get("description","").lower()

    category = "Other"
    flag = ""

    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "waterlogging" in text:
        category = "Flooding"
    elif "streetlight" in text or "light not working" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text:
        category = "Waste"
    elif "noise" in text:
        category = "Noise"
    elif "road damage" in text or "broken road" in text:
        category = "Road Damage"
    elif "heritage" in text or "monument" in text:
        category = "Heritage Damage"
    elif "heat" in text:
        category = "Heat Hazard"
    elif "drain" in text or "sewage" in text:
        category = "Drain Blockage"
    else:
        flag = "NEEDS_REVIEW"

    # Priority detection
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"
            break

    # Reason referencing the complaint text
    reason = f"Detected keywords in complaint: {text[:40]}"

    return {
        "complaint_id": row.get("complaint_id",""),
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

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id",""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Row processing failed",
                    "flag": "NEEDS_REVIEW"
                })

    fieldnames = ["complaint_id","category","priority","reason","flag"]

    with open(output_path,"w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")