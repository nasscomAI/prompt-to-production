"""
UC-0A — Complaint Classifier
A lightweight rule-based implementation that follows the UC-0A schema.
"""
import argparse
import csv
import re
from typing import Dict, List

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

CATEGORY_RULES: List[tuple[str, List[str]]] = [
    ("Pothole", [r"\bpothole\b", r"\bpotholed\b"]),
    ("Flooding", [r"\bflood\w*\b", r"\bwaterlogged\b", r"\bsubmerged\b"]),
    ("Streetlight", [r"\bstreetlight\b", r"\blight\b", r"\bglow\b", r"\bflicker\w*\b"]),
    ("Waste", [r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\boverflowing\b"]),
    ("Noise", [r"\bnoise\b", r"\bmusic\b", r"\bloud\b"]),
    ("Road Damage", [r"\broad\b", r"\bcrack\w*\b", r"\bfootpath\b", r"\btiles\b", r"\bsinking\b"]),
    ("Heritage Damage", [r"\bheritage\b", r"\bheritage\s+street\b"]),
    ("Heat Hazard", [r"\bheat\b", r"\bhot\b", r"\btemperature\b"]),
    ("Drain Blockage", [r"\bdrain\b", r"\bmanhole\b", r"\bblock\w*\b"]),
]


def _match_category(description: str) -> str:
    if not description:
        return "Other"

    normalized = description.lower()
    matched_categories = []
    for category, patterns in CATEGORY_RULES:
        if any(re.search(pattern, normalized) for pattern in patterns):
            matched_categories.append(category)

    if not matched_categories:
        return "Other"

    priority_order = [
        "Pothole",
        "Flooding",
        "Streetlight",
        "Waste",
        "Noise",
        "Road Damage",
        "Heritage Damage",
        "Heat Hazard",
        "Drain Blockage",
    ]
    for category in priority_order:
        if category in matched_categories:
            return category
    return matched_categories[0]


def _build_reason(description: str, category: str, priority: str) -> str:
    if not description:
        return "No description was provided, so the complaint was marked for review."

    matched_terms = [term for term in re.split(r"[^a-zA-Z]+", description.lower()) if term]
    keywords = []
    for term in matched_terms:
        if term in {"pothole", "flood", "streetlight", "waste", "noise", "road", "heritage", "heat", "drain", "block", "school", "hazard", "injury", "child", "hospital", "ambulance", "fire", "fell", "collapse"}:
            keywords.append(term)
        elif len(term) > 4 and term not in {"large", "near", "after", "during", "cause", "risk", "area", "days", "hours", "water", "public"}:
            keywords.append(term)
    if not keywords:
        keywords = ["description"]

    selected_keywords = keywords[:3]
    return f"The description mentions {', '.join(selected_keywords)} and supports the {category} category with {priority.lower()} priority."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag.
    """
    description = (row.get("description") or row.get("complaint_description") or "").strip()
    complaint_id = row.get("complaint_id", "")
    category = _match_category(description)

    lowered = description.lower()
    is_urgent = any(keyword in lowered for keyword in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"

    flag = ""
    if not description:
        category = "Other"
        priority = "Low"
        flag = "NEEDS_REVIEW"
    elif category == "Other":
        flag = "NEEDS_REVIEW"
    elif category in {"Road Damage", "Drain Blockage"} and not any(word in lowered for word in ["road", "drain", "manhole", "block", "crack", "footpath", "tiles"]):
        flag = "NEEDS_REVIEW"

    reason = _build_reason(description, category, priority)
    return {
        "complaint_id": complaint_id,
        "category": category if category in ALLOWED_CATEGORIES else "Other",
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    The function never crashes on a bad row; it writes a fallback result instead.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "The row could not be classified reliably.",
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
