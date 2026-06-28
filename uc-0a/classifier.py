"""
UC-0A — Complaint Classifier
CRAFT-enforced: taxonomy drift, severity blindness, missing justification, ambiguity flagging.
"""
import argparse
import csv
import sys

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole", "pot hole", "crater", "tyre damage"],
    "Flooding":        ["flood", "flooded", "flooding", "waterlogged", "submerged", "knee-deep", "standing water"],
    "Streetlight":     ["streetlight", "street light", "lamp", "light out", "dark", "lighting", "no light"],
    "Waste":           ["garbage", "waste", "trash", "litter", "dumping", "rubbish", "open dump"],
    "Noise":           ["noise", "loud", "sound", "music", "honking", "disturbance"],
    "Road Damage":     ["road damage", "road crack", "broken road", "damaged road", "road broken", "caved in", "road surface"],
    "Heritage Damage": ["heritage", "monument", "heritage site", "historical", "ancient"],
    "Heat Hazard":     ["heat", "temperature", "hot", "heat wave", "heatwave"],
    "Drain Blockage":  ["drain", "drainage", "blocked drain", "sewer", "manhole", "clogged"],
}


def _detect_categories(description: str) -> list:
    text = description.lower()
    matched = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            matched.append(category)
    return matched


def _detect_severity(description: str) -> bool:
    text = description.lower()
    return any(kw in text for kw in SEVERITY_KEYWORDS)


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    matched = _detect_categories(description)

    if len(matched) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched) == 1:
        category = matched[0]
        flag = ""
    else:
        # Ambiguous — pick first match but flag for review
        category = matched[0]
        flag = "NEEDS_REVIEW"

    is_urgent = _detect_severity(description)
    priority = "Urgent" if is_urgent else "Standard"

    # Build reason citing specific words from description
    words = description.split()
    excerpt = " ".join(words[:12]) + ("..." if len(words) > 12 else "")
    reason = f"Classified as {category} based on description: \"{excerpt}\""
    if is_urgent:
        triggered = [kw for kw in SEVERITY_KEYWORDS if kw in description.lower()]
        reason += f"; marked Urgent due to keyword(s): {', '.join(triggered)}."
    else:
        reason += "."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            if not row.get("complaint_id", "").strip():
                print(f"Warning: skipping row with missing complaint_id: {row}", file=sys.stderr)
                continue
            try:
                result = classify_complaint(row)
            except Exception as exc:
                print(f"Error classifying {row.get('complaint_id')}: {exc}", file=sys.stderr)
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification failed: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
