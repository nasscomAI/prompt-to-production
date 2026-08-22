"""
UC-0A — Complaint Classifier
Rule-based classification per agents.md — no free-form LLM guessing at inference time.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Every category whose phrase appears in the description is a candidate — see
# _detect_categories. A description matching more than one is genuinely ambiguous,
# not a case to silently pick a winner for.
CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood"]),
    ("Drain Blockage", ["manhole", "drain block"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "lamp"]),
    ("Waste", ["garbage", "bulk waste", "dead animal", "overflowing", "trash"]),
    ("Noise", ["playing music", "loud noise", "noise complaint"]),
    ("Road Damage", ["road surface", "footpath"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard", ["heatwave", "heat wave", "extreme heat"]),
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

RESULT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _detect_categories(description_lower: str) -> list:
    return [
        category
        for category, phrases in CATEGORY_KEYWORDS
        if any(phrase in description_lower for phrase in phrases)
    ]


def _detect_severity_hits(description_lower: str) -> list:
    return [kw for kw in SEVERITY_KEYWORDS if re.search(rf"\b{kw}\b", description_lower)]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()
    candidates = _detect_categories(description_lower)
    severity_hits = _detect_severity_hits(description_lower)
    priority = "Urgent" if severity_hits else "Standard"

    if len(candidates) == 0:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f'No category keywords matched description: "{description}"',
            "flag": "NEEDS_REVIEW",
        }

    if len(candidates) > 1:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f"Ambiguous — description matches multiple categories {candidates}; needs human judgement.",
            "flag": "NEEDS_REVIEW",
        }

    category = candidates[0]
    reason = (
        f"Matched '{category}'; severity keyword(s) {severity_hits} triggered Urgent."
        if severity_hits
        else f"Matched '{category}'; no severity keywords present."
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def _safe_classify(row: dict) -> dict:
    """Never let one bad row abort the batch — degrade to a flagged Other row instead."""
    try:
        return classify_complaint(row)
    except Exception as exc:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": f"Classification error: {exc}",
            "flag": "NEEDS_REVIEW",
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        rows = list(csv.DictReader(infile))

    results = [_safe_classify(row) for row in rows]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
