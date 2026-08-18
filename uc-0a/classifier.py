"""
UC-0A — Complaint Classifier
Built following the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from typing import Dict, Tuple

# Allowed taxonomy values strictly enforced per README.md & agents.md
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

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

# Category matching patterns (regex or keywords)
CATEGORY_PATTERNS = {
    "Pothole": [r"\bpothole\b", r"\bcrater\b"],
    "Flooding": [r"\bflood", r"\bwaterlogging\b", r"\binundat", r"\bstanding in water\b"],
    "Streetlight": [r"\bstreetlight\b", r"\bstreet light\b", r"\blights out\b", r"\bflickering\b", r"\bdark at night\b"],
    "Waste": [r"\bgarbage\b", r"\bwaste\b", r"\bdumped\b", r"\btrash\b", r"\bdead animal\b", r"\bins\b"],
    "Noise": [r"\bmusic\b", r"\bnoise\b", r"\bloudspeaker\b", r"\bmidnight\b", r"\bsound\b"],
    "Heritage Damage": [r"\bheritage\b", r"\bmonument\b", r"\bhistoric\b"],
    "Heat Hazard": [r"\bheat\b", r"\bheatwave\b", r"\bsunstroke\b", r"\bthermal\b"],
    "Drain Blockage": [r"\bdrain\b", r"\bdrainage\b", r"\bgutter\b", r"\bsewer\b", r"\bmanhole\b", r"\bclogged\b"],
    "Road Damage": [r"\bcracked\b", r"\bsinking\b", r"\bfootpath\b", r"\btiles broken\b", r"\broad surface\b", r"\bupturned\b", r"\basphalt\b", r"\btar\b"],
}


def _determine_category_and_flag(desc: str) -> Tuple[str, str, str]:
    """
    Determine category, flag, and matching text fragment.
    Returns (category, flag, fragment_cited)
    """
    desc_lower = desc.lower()
    matched_categories = []
    matched_fragments = {}

    for cat, patterns in CATEGORY_PATTERNS.items():
        for pat in patterns:
            match = re.search(pat, desc_lower)
            if match:
                matched_categories.append(cat)
                matched_fragments[cat] = desc[match.start():match.end()]
                break

    if len(matched_categories) == 1:
        cat = matched_categories[0]
        return cat, "", f"contains '{matched_fragments[cat]}'"
    elif len(matched_categories) > 1:
        # Ambiguous complaint matching multiple categories -> flag NEEDS_REVIEW
        primary_cat = matched_categories[0]
        cite = f"contains '{matched_fragments[primary_cat]}'"
        return primary_cat, "NEEDS_REVIEW", cite
    else:
        # No clear category matched
        return "Other", "NEEDS_REVIEW", "description lacks specific category keywords"


def _determine_priority(desc: str) -> Tuple[str, str]:
    """
    Determine priority based on severity keywords.
    Returns (priority, keyword_cited_if_any)
    """
    desc_lower = desc.lower()
    for kw in SEVERITY_KEYWORDS:
        match = re.search(r"\b" + re.escape(kw) + r"s?\b", desc_lower)
        if match:
            cited_kw = desc[match.start():match.end()]
            return "Urgent", cited_kw

    return "Standard", ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip() if row else ""
    description = row.get("description", "").strip() if row else ""

    # Error handling for missing / empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    category, flag, cat_cite = _determine_category_and_flag(description)
    priority, kw_cite = _determine_priority(description)

    # Build single sentence reason citing specific words from description
    if priority == "Urgent":
        reason = f"Classified as {category} with Urgent priority because description mentions '{kw_cite}' and {cat_cite}."
    else:
        reason = f"Classified as {category} with Standard priority because description {cat_cite}."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception as e:
                    complaint_id = row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN"
                    result = {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row could not be parsed: {str(e)}",
                        "flag": "NEEDS_REVIEW",
                    }
                results.append(result)
    except Exception as e:
        print(f"Error opening or reading input CSV file {input_path}: {e}")
        return

    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output CSV file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

