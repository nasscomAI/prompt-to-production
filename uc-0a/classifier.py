"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re
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


def _normalize_text(value: str | None) -> str:
    return (value or "").strip()


def _detect_category(description: str) -> tuple[str, bool]:
    text = description.lower()

    if any(term in text for term in ["pothole", "tyre damage"]):
        return "Pothole", False

    if any(term in text for term in ["flood", "flooded", "waterlogged", "underpass", "inundated", "overflowing", "stagnant"]):
        return "Flooding", False

    if any(term in text for term in ["streetlight", "street light", "lights out", "flickering", "sparking", "dark"]):
        return "Streetlight", False

    if any(term in text for term in ["garbage", "waste", "rubbish", "bins", "dumped", "trash", "bulk waste"]):
        return "Waste", False

    if any(term in text for term in ["noise", "music", "loud", "noisy", "sound", "disturbance"]):
        return "Noise", False

    if any(term in text for term in ["cracked", "crack", "footpath", "tiles broken", "upturned", "sinking", "surface damage"]):
        return "Road Damage", False

    if any(term in text for term in ["heritage", "monument"]):
        return "Heritage Damage", False

    if any(term in text for term in ["heat", "hot", "temperature", "sun"]):
        return "Heat Hazard", False

    if any(term in text for term in ["drain", "drainage", "manhole", "blocked drain", "blockage", "sewer"]):
        return "Drain Blockage", False

    return "Other", True


def _build_reason(description: str, category: str) -> str:
    text = description.strip()
    if not text:
        return "The description does not provide enough detail for a confident classification."

    match = None
    for phrase in ["pothole", "flooded", "streetlight", "garbage", "music", "crack", "heritage", "heat", "drain", "hazard", "injury", "fell", "school", "hospital", "ambulance", "fire"]:
        if phrase.lower() in text.lower():
            match = phrase
            break

    if match:
        return f"The description mentions '{match}' and supports the category '{category}'."

    return f"The description says '{text[:80].rstrip()}' and supports the category '{category}'."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = _normalize_text(row.get("complaint_id"))
    description = _normalize_text(row.get("description"))

    category, needs_review = _detect_category(description)
    if category not in ALLOWED_CATEGORIES:
        category = "Other"

    if any(re.search(rf"\b{re.escape(keyword)}\b", description, re.IGNORECASE) for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif category in {"Noise", "Waste"}:
        priority = "Low"
    else:
        priority = "Standard"

    reason = _build_reason(description, category)
    flag = "NEEDS_REVIEW" if needs_review else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results CSV.
    The function continues even when a row is malformed or missing content.
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with input_file.open("r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = []
        for row in reader:
            try:
                rows.append(classify_complaint(row))
            except Exception:
                rows.append(
                    {
                        "complaint_id": _normalize_text(row.get("complaint_id")) if row else "",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "The row could not be classified reliably.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with output_file.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
