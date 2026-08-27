"""UC-0A complaint classifier for municipal service tickets."""

import argparse
import csv
from pathlib import Path

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
    "Other",
]

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
    ("Heritage Damage", ["heritage", "historic", "old city area", "heritage street"]),
    ("Pothole", ["pothole", "tyre damage", "road damage"]),
    ("Flooding", ["flooded", "flooding", "flood", "waterlogged", "underpass", "rain", "inundated"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "lamp", "flickering", "sparking", "dark at night"]),
    ("Waste", ["garbage", "waste", "overflowing bins", "dumped", "refuse", "dead animal", "bulk waste"]),
    ("Noise", ["noise", "music past midnight", "loud music", "sound", "noisy"]),
    ("Road Damage", ["road surface", "cracked", "tiles broken", "broken footpath", "upturned", "sinking", "manhole cover missing"]),
    ("Heat Hazard", ["heat", "heatwave", "extreme temperature", "hot weather", "high temperature"]),
    ("Drain Blockage", ["drain blocked", "blocked drain", "drainage", "manhole", "sewer", "clogged drain"]),
]


def classify_complaint(row: dict) -> dict:
    """Return a classification dict for one complaint row."""
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()
    description_lower = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description was insufficient to classify the complaint.",
            "flag": "NEEDS_REVIEW",
        }

    category = "Other"
    matched_terms = []
    for candidate, keywords in CATEGORY_RULES:
        hits = [keyword for keyword in keywords if keyword in description_lower]
        if hits:
            category = candidate
            matched_terms.extend(hits)
            break

    if category == "Other":
        if any(keyword in description_lower for keyword in ["school", "hospital", "injury", "fell"]):
            category = "Road Damage"
            matched_terms = ["injury", "fell"]

    priority = "Standard"
    if any(keyword in description_lower for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"

    reason_text = description
    if matched_terms:
        evidence = ", ".join(sorted(set(matched_terms), key=lambda item: matched_terms.index(item)))
        reason_text = f'Description mentions "{evidence}" which supports the {category} classification.'
    else:
        reason_text = "Description does not provide enough direct evidence for a specific category."

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category if category in ALLOWED_CATEGORIES else "Other",
        "priority": priority,
        "reason": reason_text,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, and write results CSV."""
    input_file = Path(input_path)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    with input_file.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for raw_row in reader:
            if not raw_row:
                continue
            try:
                rows.append(classify_complaint(raw_row))
            except Exception:
                rows.append({
                    "complaint_id": raw_row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Row could not be classified safely.",
                    "flag": "NEEDS_REVIEW",
                })

    with output_file.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
