"""UC-0A — Complaint Classifier.

This app is deliberately deterministic and strict:
- categories must use the exact allowed vocabulary,
- priority becomes Urgent whenever severity terms are present,
- every row must include a reason citing the description words,
- and genuinely ambiguous rows are flagged for review instead of guessed.
"""

from __future__ import annotations

import argparse
import csv
import sys
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

URGENT_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole"],
    "Flooding": ["flood", "flooded", "waterlogged", "water log"],
    "Streetlight": ["streetlight", "street light", "lights out", "sparking", "electrical hazard"],
    "Waste": ["garbage", "waste", "overflowing bins", "dumped on public road", "dead animal"],
    "Noise": ["music", "noisy", "loud", "midnight"],
    "Road Damage": ["road surface cracked", "cracked", "sinking", "road", "surface"],
    "Heritage Damage": ["heritage", "historic", "monument"],
    "Heat Hazard": ["heat", "sun", "heat hazard"],
    "Drain Blockage": ["drain blocked", "drain blockage", "blocked drain", "manhole"],
}


def classify_complaint(row: dict) -> dict:
    description = str(row.get("description", "")).strip().lower()
    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "No usable description text was provided.",
            "flag": "NEEDS_REVIEW",
        }

    urgent_hits = [kw for kw in URGENT_KEYWORDS if kw in description]
    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in description for keyword in keywords):
            matched_categories.append(category)

    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if category not in ALLOWED_CATEGORIES:
        category = "Other"

    if urgent_hits:
        priority = "Urgent"
        reason = f"The description mentions {', '.join(urgent_hits)}; these severity words require urgent priority."
    else:
        priority = "Standard"
        reason = f"The description cites '{description[:80]}' as the basis for the classification."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"REFUSE: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with input_file.open("r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        rows = []

        for row in reader:
            try:
                rows.append(classify_complaint(row))
            except Exception as exc:
                rows.append(
                    {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row could not be classified: {exc}",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Results written to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
