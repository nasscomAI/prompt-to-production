"""
UC-0A — Complaint Classifier
Built from agents.md (enforcement rules) and skills.md (skill contracts).
"""
import argparse
import csv
import sys

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "waterlog"],
    "Streetlight": ["streetlight", "street light", "flickering", "sparking"],
    "Waste": ["garbage", "waste", "dumped", "dead animal", "bin"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath", "manhole"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke"],
    "Drain Blockage": ["drain blocked", "drain"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    matched_categories = [
        category
        for category, keywords in CATEGORY_KEYWORDS.items()
        if any(keyword in desc_lower for keyword in keywords)
    ]

    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        # Zero or multiple (ambiguous) matches — refuse to guess.
        category = "Other"
        flag = "NEEDS_REVIEW"

    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    priority = "Urgent" if matched_severity else "Standard"

    if matched_severity:
        reason = f"Marked Urgent due to keyword(s): {', '.join(matched_severity)}."
    elif len(matched_categories) == 1:
        reason = f"Classified as {category} based on keyword(s): {', '.join(CATEGORY_KEYWORDS[category])}."
    elif len(matched_categories) > 1:
        reason = f"Ambiguous: description matches multiple categories ({', '.join(matched_categories)}); flagged for manual review."
    else:
        reason = "No clear category keywords found in description; flagged for manual review."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    rows_written = 0

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        results = []
        for row in reader:
            if not row.get("complaint_id"):
                print(f"Warning: skipping row with no complaint_id: {row}", file=sys.stderr)
                continue
            try:
                result = classify_complaint(row)
            except Exception as exc:
                print(f"Warning: classify_complaint failed for {row.get('complaint_id')}: {exc}", file=sys.stderr)
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Classification failed; flagged for manual review",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)
            rows_written += 1

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return rows_written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
