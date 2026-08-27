"""
UC-0A — Complaint Classifier

Classifies citizen complaints deterministically using keyword-based rules.
Enforces agents.md: exact category, severity-driven priority, cited reason,
NEEDS_REVIEW flag on ambiguity.
"""

import argparse
import csv
import os


_URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

_CATEGORY_MATCHERS = [
    ("Pothole",         ["pothole"]),
    ("Streetlight",     ["streetlight", "street light", "lights out"]),
    ("Flooding",        ["flooded", "flooding", "floods"]),
    ("Drain Blockage",  ["drain blocked", "drain blockage",
                         "drain completely blocked", "main drain blocked",
                         "main stormwater drain"]),
    ("Waste",           ["garbage", "overflowing bins", "bins overflowing",
                         "dead animal", "waste not cleared", "piles of waste",
                         "post-market waste", "bulk waste", "waste dumped",
                         "waste overflowing"]),
    ("Noise",           ["playing music", "band playing", "club music",
                         "drilling", "idling with engines"]),
    ("Road Damage",     ["road surface", "road collapsed", "crater",
                         "cracked and sinking", "footpath tiles broken",
                         "footpath broken", "road cracked"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard",     ["heat hazard"]),
]


def _check_priority(description: str) -> str:
    desc_lower = description.lower()
    for kw in _URGENT_KEYWORDS:
        if kw in desc_lower:
            return "Urgent"
    return "Standard"


def _classify(description: str) -> tuple:
    desc_lower = description.lower()

    matched = []
    for cat_name, keywords in _CATEGORY_MATCHERS:
        for kw in keywords:
            if kw in desc_lower:
                matched.append(cat_name)
                break

    seen = set()
    unique_matched = []
    for m in matched:
        if m not in seen:
            seen.add(m)
            unique_matched.append(m)

    if len(unique_matched) == 1:
        return unique_matched[0], ""
    elif len(unique_matched) > 1:
        return "Other", "NEEDS_REVIEW"
    else:
        return "Other", "NEEDS_REVIEW"


def _build_reason(description: str) -> str:
    desc_stripped = description.strip()
    if not desc_stripped:
        return "No description provided"

    if len(desc_stripped) > 120:
        snippet = desc_stripped[:120].rsplit(" ", 1)[0] + "..."
    else:
        snippet = desc_stripped

    return f'Description states: "{snippet}"'


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns dict with complaint_id, category, priority, reason, flag.
    Enforces agents.md: 10-category keyword match, severity priority,
    cited reason, NEEDS_REVIEW on ambiguity. Empty description -> fallback.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    category, flag = _classify(description)
    priority = _check_priority(description)
    reason = _build_reason(description)

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

    Raises FileNotFoundError if input missing. Bad rows produce a fallback
    NEEDS_REVIEW row and continue. Empty input -> header-only output.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            with open(output_path, "w", newline="", encoding="utf-8") as fout:
                writer = csv.DictWriter(fout, fieldnames=fieldnames)
                writer.writeheader()
            return

        results = []
        for i, row in enumerate(reader):
            try:
                result = classify_complaint(row)
            except Exception:
                complaint_id = (
                    row.get("complaint_id", f"row_{i}") if row else f"row_{i}"
                )
                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classification failed",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
