"""
UC-0A — Complaint Classifier
Starter file. Build this using your RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
from typing import List, Tuple

CATEGORY_RULES: List[Tuple[str, List[str]]] = [
    ("Heritage Damage", ["heritage"]),
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "flooded", "underpass flooded", "water standing", "bridge approach floods", "stranded"]),
    ("Drain Blockage", ["drain blocked", "drainage", "clogged drain", "blocked drain"]),
    ("Streetlight", ["streetlight", "streetlights", "light out", "lights out", "flicker", "flickering", "sparking", "dark at night"]),
    ("Waste", ["garbage", "waste", "trash", "dumped", "bins", "dead animal", "smell", "overflowing"]),
    ("Noise", ["noise", "loud", "music", "wedding", "past midnight", "weeknights"]),
    ("Road Damage", ["cracked", "sinking", "surface cracked", "manhole cover missing", "upturned", "broken footpath", "tyre damage"]),
    ("Heat Hazard", ["heat", "hot", "heat hazard"]),
    ("Drain Blockage", ["drain blocked", "blocked drain", "drain blocked"]),
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


def _find_match(text: str, patterns: List[str]) -> List[str]:
    found = []
    for pattern in patterns:
        if pattern in text:
            found.append(pattern)
    return found


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    normalized = description.lower()

    category = "Other"
    category_matches: List[str] = []
    for candidate, patterns in CATEGORY_RULES:
        matches = _find_match(normalized, patterns)
        if matches:
            category = candidate
            category_matches = matches
            break

    if category == "Other":
        if any(keyword in normalized for keyword in ["manhole", "footpath", "bridge", "road", "tyre"]):
            category = "Road Damage"
            category_matches = ["road"]

    priority = "Urgent" if any(keyword in normalized for keyword in SEVERITY_KEYWORDS) else "Standard"
    if category == "Noise" and priority == "Standard":
        priority = "Low"

    if category_matches:
        reason_phrase = category_matches[0]
    else:
        reason_phrase = description[:60] if description else "no descriptive text"

    reason = f"Description mentions '{reason_phrase}'."
    if priority == "Urgent" and not any(keyword in normalized for keyword in SEVERITY_KEYWORDS):
        reason = f"Marked urgent due to strong severity signals and description mentions '{reason_phrase}'."

    flag = ""
    if category == "Other" or not description:
        flag = "NEEDS_REVIEW"

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
    with open(input_path, newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

        with open(output_path, "w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            for row_number, row in enumerate(reader, start=2):
                try:
                    result = classify_complaint(row)
                except Exception as exc:
                    sys.stderr.write(f"Row {row_number}: error classifying complaint: {exc}\n")
                    result = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Failed to classify complaint due to invalid row.",
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
