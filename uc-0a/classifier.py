"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
from pathlib import Path

ALLOWED_CATEGORIES = {
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
}

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

CATEGORY_RULES = [
    ("Pothole", ["pothole", "tyre damage", "road damage"]),
    ("Flooding", ["flood", "flooded", "water", "underpass", "inundated"]),
    ("Streetlight", ["streetlight", "streetlights", "light out", "dark at night", "sparking"]),
    ("Waste", ["garbage", "waste", "overflowing", "bins", "dumped"]),
    ("Noise", ["noise", "music", "loud", "midnight"]),
    ("Road Damage", ["cracked", "sinking", "footpath", "tiles broken", "upturned", "road surface"]),
    ("Heritage Damage", ["heritage", "historic"]),
    ("Heat Hazard", ["heat", "heatwave", "temperature"]),
    ("Drain Blockage", ["drain", "blocked", "blockage", "clogged"]),
]


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row using the UC-0A schema."""
    description = ""
    for key in ("description", "Description", "desc"):
        if row.get(key):
            description = str(row[key])
            break

    complaint_id = row.get("complaint_id", "")
    lower_description = description.lower()

    matched_categories = []
    for category, keywords in CATEGORY_RULES:
        if any(keyword in lower_description for keyword in keywords):
            matched_categories.append(category)

    if matched_categories:
        category = matched_categories[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if any(keyword in lower_description for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif "noise" in lower_description or "music" in lower_description:
        priority = "Low"
    else:
        priority = "Standard"

    if matched_categories and len(matched_categories) > 1:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    evidence = None
    for token in ["pothole", "flooded", "streetlight", "garbage", "music", "cracked", "heritage", "heat", "drain", "hazard"]:
        if token in lower_description:
            evidence = token
            break

    if evidence:
        reason = f"The description mentions '{evidence}', which supports the {category} classification."
    else:
        reason = f"The description is consistent with the {category} classification."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, and write a results CSV."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = []
        for row in reader:
            try:
                rows.append(classify_complaint(row))
            except Exception:
                rows.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "The row could not be classified reliably.",
                    "flag": "NEEDS_REVIEW",
                })

    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
