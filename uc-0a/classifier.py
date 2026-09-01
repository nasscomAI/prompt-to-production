"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.
"""
import argparse
import csv
import re
import sys
from typing import Dict, List, Tuple


ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Pothole": ["pothole", "potholes", "road hole", "road has hole", "road has a hole", "pit in road", "road pit", "road surface broken", "road collapsed", "road has collapsed"],
    "Flooding": ["flood", "flooding", "waterlogged", "water logging", "water standing", "water stagnation", "inundated", "submerged", "water on road", "heavy water"],
    "Streetlight": ["streetlight", "street light", "streetlamp", "street lamp", "light not working", "light off", "lights out", "light out", "no light", "dark road", "lamp post", "pole light"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "litter", "dump", "dumping", "waste disposal", "garbage dump", "garbage pile", "garbage collection", "refuse", "sewage waste"],
    "Noise": ["noise", "noisy", "loud", "loudspeaker", "music", "honking", "blaring", "sound", "disturbance", "loud noise"],
    "Road Damage": ["road damage", "road broken", "road needs repair", "road repair", "road condition", "asphalt", "road surface", "tarmac", "road crumbled", "road crumble"],
    "Heritage Damage": ["heritage", "monument", "temple", "historical", "ancient", "heritage site", "heritage structure", "heritage building", "heritage wall", "heritage damage"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke", "heat stroke", "hot", "scorching", "extreme heat", "heat exhaustion", "heat wave"],
    "Drain Blockage": ["drain", "drainage", "clogged", "blocked drain", "choked drain", "sewer", "sewerage", "storm drain", "gutter", "drain blocked", "drain clogged", "sewage overflow", "sewage blockage"],
}


def _find_category(description: str) -> Tuple[str, bool]:
    """
    Match description against CATEGORY_KEYWORDS.
    Returns (category, is_ambiguous) where is_ambiguous is True if
    description matches multiple categories equally.
    """
    desc_lower = description.lower()
    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                break

    if len(matched_categories) == 0:
        return ("Other", True)
    elif len(matched_categories) == 1:
        return (matched_categories[0], False)
    else:
        return (matched_categories[0], True)


def _extract_reason(description: str, category: str) -> str:
    """
    Extract a reason citing specific words from the description.
    Returns one sentence with a quoted fragment from the original text.
    """
    desc_stripped = description.strip()
    if not desc_stripped:
        return "No description provided."

    if len(desc_stripped) <= 120:
        return f'Complaint states "{desc_stripped}" which indicates {category}.'

    keywords = CATEGORY_KEYWORDS.get(category, [])
    for kw in keywords:
        idx = desc_stripped.lower().find(kw)
        if idx != -1:
            start = max(0, idx - 30)
            end = min(len(desc_stripped), idx + len(kw) + 30)
            snippet = desc_stripped[start:end].strip()
            if start > 0:
                snippet = "..." + snippet
            if end < len(desc_stripped):
                snippet = snippet + "..."
            return f'Complaint mentions "{snippet}" which indicates {category}.'

    return f'Complaint describes "{desc_stripped[:80]}..." which indicates {category}.'


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "") or "UNKNOWN"
    description = row.get("description", "") or ""

    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _find_category(description)

    desc_lower = description.lower()
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"

    reason = _extract_reason(description, category)

    flag = "NEEDS_REVIEW" if is_ambiguous else ""

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
    Never skips rows. Never crashes on bad input.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    classified_count = 0
    flagged_count = 0

    try:
        with open(input_path, "r", newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()
        return
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()
        return

    results: List[dict] = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception:
            result = {
                "complaint_id": row.get("complaint_id", "") or "UNKNOWN",
                "category": "Other",
                "priority": "Standard",
                "reason": "Row could not be classified.",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)
        classified_count += 1
        if result["flag"] == "NEEDS_REVIEW":
            flagged_count += 1

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {classified_count} rows. {flagged_count} flagged for review.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
