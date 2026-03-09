"""
UC-0A — Complaint Classifier
RICE-enforced rule-based classifier.
"""

import argparse
import csv

URGENCY_KEYWORDS = [
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

CATEGORY_RULES = [
    (
        "Drain Blockage",
        ["drain", "drainage", "blocked drain", "sewer", "stormwater", "nala"],
    ),
    (
        "Flooding",
        ["flood", "flooded", "flooding", "waterlog", "submerged", "inundated", "rain"],
    ),
    ("Pothole", ["pothole", "pot hole", "crater", "road depression"]),
    (
        "Streetlight",
        ["streetlight", "street light", "lamp", "lighting", "dark road", "no light"],
    ),
    ("Waste", ["garbage", "waste", "trash", "dumping", "litter", "rubbish", "dump"]),
    ("Noise", ["noise", "loud", "sound", "music", "construction noise", "honking"]),
    (
        "Road Damage",
        ["road damage", "broken road", "damaged road", "pavement", "road crack", "tar"],
    ),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient"]),
    ("Heat Hazard", ["heat", "temperature", "hot", "thermal", "heat wave"]),
]

STANDARD_KEYWORDS = [
    "suffering",
    "blocked",
    "diverted",
    "risk",
    "concern",
    "severe",
    "overflow",
    "dengue",
    "breeding",
    "loss",
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()

    if not desc:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    # Match categories
    matched = [
        (cat, kws) for cat, kws in CATEGORY_RULES if any(kw in desc_lower for kw in kws)
    ]

    if len(matched) == 0:
        category, flag, cited_kw = "Other", "", None
    elif len(matched) == 1:
        category, flag = matched[0][0], ""
        cited_kw = next(kw for kw in matched[0][1] if kw in desc_lower)
    else:
        category, flag = matched[0][0], "NEEDS_REVIEW"
        cited_kw = next(kw for kw in matched[0][1] if kw in desc_lower)

    # Priority
    urgent_hit = next((kw for kw in URGENCY_KEYWORDS if kw in desc_lower), None)
    if urgent_hit:
        priority = "Urgent"
    elif any(kw in desc_lower for kw in STANDARD_KEYWORDS):
        priority = "Standard"
    else:
        priority = "Low"

    # Reason
    if urgent_hit:
        reason = f"Description contains '{urgent_hit}', indicating life-risk and requiring urgent response."
    elif cited_kw:
        reason = (
            f"Description contains '{cited_kw}', indicating a {category.lower()} issue."
        )
    else:
        reason = f"Classified as {category} based on overall description context."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("Empty input file.")
        return

    results = []
    for row in rows:
        print(f"Classifying {row.get('complaint_id')}...", end=" ")
        try:
            result = classify_complaint(row)
        except Exception as e:
            print(f"  Error: {e}")
            result = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": "Classification failed.",
                "flag": "NEEDS_REVIEW",
            }
        row.update(result)
        results.append(row)
        print(f"{result['category']} | {result['priority']}")

    fieldnames = list(rows[0].keys())
    for f in ["category", "priority", "reason", "flag"]:
        if f not in fieldnames:
            fieldnames.append(f)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
