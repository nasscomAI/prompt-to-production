"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re
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
SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)
OUTPUT_COLUMNS = ["complaint_id", "category", "priority", "reason", "flag"]


def _contains(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)


def _quoted_terms(description: str, terms: list[str]) -> str:
    found = []
    lowered = description.lower()
    for term in terms:
        if term.lower() in lowered and term not in found:
            found.append(term)
    if not found:
        words = re.findall(r"[\w–-]+", description)[:5]
        found = [" ".join(words) if words else "description"]
    return ", ".join(f'"{term}"' for term in found[:3])


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()
    if not complaint_id:
        raise ValueError("Missing complaint_id")
    if not description:
        raise ValueError(f"{complaint_id}: missing description")

    text = description.casefold()
    category = "Other"
    flag = ""
    reason_terms: list[str] = []

    if _contains(text, "pothole"):
        category = "Pothole"
        reason_terms.append("pothole")
    elif _contains(text, "flood", "rainwater", "draining", "drainage"):
        category = "Flooding"
        reason_terms.extend([term for term in ["rainwater", "draining", "flood"] if term in text])
    elif _contains(text, "streetlight", "lamp post", "darkness", "substation", "tripped"):
        category = "Streetlight"
        reason_terms.extend([term for term in ["lamp post", "darkness", "substation", "tripped"] if term in text])
    elif _contains(text, "waste", "overflowing", "piles"):
        category = "Waste"
        reason_terms.extend([term for term in ["waste", "overflowing", "piles"] if term in text])
    elif _contains(text, "amplifier", "playing", "band", "noise"):
        category = "Noise"
        reason_terms.extend([term for term in ["amplifiers", "band", "playing", "11pm"] if term.casefold() in text])
    elif _contains(text, "heritage", "historic", "museum", "cobblestones", "stone", "defaced"):
        category = "Heritage Damage"
        reason_terms.extend([term for term in ["heritage", "Historic", "Museum", "cobblestones", "stone", "defaced"] if term.casefold() in text])
    elif _contains(text, "heat", "heatwave"):
        category = "Heat Hazard"
        reason_terms.extend([term for term in ["heat", "heatwave"] if term in text])
    elif _contains(text, "drain block", "blocked drain", "drain clogged"):
        category = "Drain Blockage"
        reason_terms.append("drain")
    elif _contains(text, "road", "footpath", "surface", "buckled", "subsided", "paving"):
        category = "Road Damage"
        reason_terms.extend([term for term in ["road", "footpath", "surface", "buckled", "subsided", "paving"] if term in text])
    else:
        flag = "NEEDS_REVIEW"

    priority = "Urgent" if any(keyword in text for keyword in SEVERITY_KEYWORDS) else "Standard"
    if category == "Other" and flag == "NEEDS_REVIEW" and priority != "Urgent":
        priority = "Low"

    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"{complaint_id}: invalid category {category}")

    reason = f"Classified as {category} because the description mentions {_quoted_terms(description, reason_terms)}."
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
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"complaint_id", "description"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Input CSV missing required columns: {', '.join(sorted(missing))}")
        rows = list(reader)

    if not rows:
        raise ValueError("Input CSV contains no complaint rows")

    results = [classify_complaint(row) for row in rows]
    target = Path(output_path)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    try:
        batch_classify(args.input, args.output)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Done. Results written to {args.output}")
