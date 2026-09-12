"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE -> agents.md -> skills.md workflow.
"""

import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "children", "school",
    "accident", "hospital", "fire", "collapse", "danger",
    "unsafe", "electrocution", "flood", "drown",
]


def detect_category(description):
    """Match description text to one of the allowed category strings."""
    text = description.lower()

    if "pothole" in text:
        return "Pothole"
    if "flood" in text or "waterlog" in text:
        return "Flooding"
    if "streetlight" in text or "street light" in text or "lamp" in text:
        return "Streetlight"
    if "waste" in text or "garbage" in text or "trash" in text:
        return "Waste"
    if "noise" in text:
        return "Noise"
    if "road" in text and ("damage" in text or "crack" in text or "broken" in text):
        return "Road Damage"
    if "heritage" in text:
        return "Heritage Damage"
    if "heat" in text:
        return "Heat Hazard"
    if "drain" in text or "sewage" in text or "blockage" in text:
        return "Drain Blockage"
    return "Other"


def detect_priority(description):
    """Return Urgent if severity keywords are present, else Standard."""
    text = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            return "Urgent"
    return "Standard"


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason
    """
    description = row.get("description", "") or ""
    complaint_id = row.get("complaint_id", "")

    category = detect_category(description)
    priority = detect_priority(description)

    # Reason must cite specific words from the description.
    reason = f"Classified based on description text: \"{description.strip()}\""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "FLAGGED: missing description field",
                    })
                    continue

                classified = classify_complaint(row)
                results.append(classified)

            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"FLAGGED: error during classification ({e})",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Results written to {output_path}")
    print(f"Rows processed: {len(results)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)