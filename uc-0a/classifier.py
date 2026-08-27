"""
UC-0A — Complaint Classifier.

The implementation uses a small keyword-based classifier that follows the workshop
rules: it maps complaints to the allowed categories, assigns Urgent priority when
severity keywords are present, writes a one-sentence reason that cites description
words, and sets NEEDS_REVIEW for genuinely ambiguous rows.
"""
import argparse
import csv
from pathlib import Path
from typing import Dict, List

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


def infer_category(description: str) -> str:
    text = description.lower()
    if "pothole" in text:
        return "Pothole"
    if "flood" in text or "flooded" in text or "water" in text and "drain" in text:
        return "Flooding"
    if "drain" in text or "manhole" in text or "blocked" in text and "drain" in text:
        return "Drain Blockage"
    if "streetlight" in text or "streetlights" in text or "lights out" in text or "light" in text and "out" in text:
        return "Streetlight"
    if "waste" in text or "garbage" in text or "bins" in text or "bulk waste" in text:
        return "Waste"
    if "noise" in text or "music" in text or "midnight" in text or "loud" in text:
        return "Noise"
    if "road" in text or "crack" in text or "surface" in text or "footpath" in text or "broken" in text:
        return "Road Damage"
    if "heritage" in text:
        return "Heritage Damage"
    if "heat" in text or "sun" in text or "hot" in text or "temperature" in text:
        return "Heat Hazard"
    return "Other"


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """Classify a single complaint row."""
    description = row.get("description", "") or ""
    category = infer_category(description)
    lowered = description.lower()
    priority = "Urgent" if any(keyword in lowered for keyword in SEVERITY_KEYWORDS) else "Standard"
    flag = ""

    if category == "Other" or ("heritage" in lowered and "light" in lowered):
        flag = "NEEDS_REVIEW"

    if category == "Other":
        reason = "The description does not clearly match one of the allowed categories, so it is marked for review."
    else:
        # Pick a few descriptive words from the description to cite.
        words = [word for word in lowered.replace(".", " ").split() if len(word) > 3][:3]
        cited_words = ", ".join(words) if words else "the report"
        reason = f"The description mentions {cited_words}, which matches the {category} category."

    if priority == "Urgent":
        urgent_hits = [keyword for keyword in SEVERITY_KEYWORDS if keyword in lowered]
        if urgent_hits:
            reason = f"The description includes urgency words such as '{urgent_hits[0]}' and supports an Urgent priority."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Read input CSV, classify each row, and write results CSV."""
    input_file = Path(input_path)
    output_file = Path(output_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with input_file.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    output_rows = []
    for row in rows:
        try:
            output_rows.append(classify_complaint(row))
        except Exception:
            output_rows.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": "The row could not be classified confidently and was marked for review.",
                "flag": "NEEDS_REVIEW",
            })

    with output_file.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Done. Results written to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
