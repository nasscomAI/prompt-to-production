"""
UC-0A — Complaint Classifier
Starter file. Build this using your RICE → agents.md → skills.md → CRAFT workflow.
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
    ("Heritage Damage", ["heritage", "heritage street", "historic"]),
    ("Drain Blockage", ["drain blocked", "drain blockage", "drain blocked", "blocked drain", "drain blocked"]),
    ("Flooding", ["flood", "flooded", "waterlogged", "standing in water", "knee-deep", "inundated"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "light out", "flickering", "sparking", "dark at night"]),
    ("Pothole", ["pothole", "hole in road", "pot hole", "tyre damage", "tire damage"]),
    ("Waste", ["garbage", "trash", "waste", "dump", "dumped", "bin", "bins", "dead animal", "refuse", "bulk waste"]),
    ("Noise", ["music", "noise", "loud", "sound", "night music", "past midnight", "late night"]),
    ("Heat Hazard", ["heat", "hot", "temperature", "scorching", "sunny", "heat hazard"]),
    ("Road Damage", ["cracked", "sinking", "broken", "upturned", "road surface", "footpath", "manhole cover missing", "bridge approach"]),
]


def _find_matching_category(description: str) -> tuple[str, str] | tuple[None, None]:
    lowered = description.lower()

    for category, patterns in CATEGORY_RULES:
        for pattern in patterns:
            if pattern in lowered:
                return category, pattern

    return None, None


def _is_urgent(description: str) -> bool:
    lowered = description.lower()
    return any(keyword in lowered for keyword in SEVERITY_KEYWORDS)


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row."""
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing complaint description; cannot classify reliably.",
            "flag": "NEEDS_REVIEW",
        }

    category, matched_phrase = _find_matching_category(description)
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = (
            "Description is ambiguous for exact category assignment; assigned Other and flagged NEEDS_REVIEW."
        )
    else:
        flag = ""
        reason = f"Classified as {category} because description mentions '{matched_phrase}'."

    priority = "Urgent" if _is_urgent(description) else "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as infile, open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Error processing row; assigned Other and flagged NEEDS_REVIEW.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
