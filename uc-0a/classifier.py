#!/usr/bin/env python3
"""
UC-0A — Municipal Complaint Classifier

Classifies citizen complaints by category, priority, reason, and flag
using keyword-based rules derived from the municipal taxonomy.

Usage:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""

import csv
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SEVERITY_KEYWORDS: List[str] = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Ordered rules — first match wins.
# More specific or higher-priority categories are placed earlier.
CATEGORY_RULES: List[Tuple[str, List[str]]] = [
    ("Pothole",         ["pothole", "pot hole", "pot-hole"]),
    ("Heritage Damage", ["heritage", "historic", "cobblestone"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlog", "waterlogged",
                         "knee-deep", "standing in water", "submerged", "inundated"]),
    ("Drain Blockage",  ["drain block", "blocked drain", "drain clog", "drain choke",
                         "sewer block", "blocked sewer", "stormwater drain",
                         "drain 100%", "drain filled"]),
    ("Streetlight",     ["streetlight", "street light", "street-light", "lamp post",
                         "light out", "lights out", "flickering", "sparking",
                         "unlit", "darkness", "wiring theft", "no light"]),
    ("Waste",           ["garbage", "overflowing bin", "dead animal", "bulk waste",
                         "waste dumped", "trash", "rubbish", "refuse", "litter",
                         "dumped on public", "waste not cleared", "waste overflow",
                         "bins overflowing", "waste bins", "not removed",
                         "waste not", "not cleared"]),
    ("Noise",           ["noise", "loud music", "music past", "blaring", "playing music",
                         "audible at", "band playing", "amplifier", "drilling from",
                         "trucks idling", "music audible"]),
    ("Heat Hazard",     ["heat hazard", "heat wave", "heatwave", "extreme heat",
                         "heat stress", "melting", "temperature", "unbearable heat",
                         "storing heat", "dangerous heat"]),
    ("Road Damage",     ["road surface", "cracked and sinking", "manhole", "footpath",
                         "tiles broken", "pavement", "surface cracked", "road damage",
                         "utility work", "sinking near", "subsided", "road collapsed",
                         "collapsed partially", "crater", "buckled", "upturned paving",
                         "broken paving", "paving removed", "road subsid"]),
]


def find_severity_trigger(description: str) -> Optional[str]:
    """Return the first severity keyword found in the description, or None."""
    desc_lower = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if keyword in desc_lower:
            return keyword
    return None


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """
    Classify a single complaint row.

    Returns a dict with keys: category, priority, reason, flag.
    """
    description = row.get("description", "").strip()

    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()
    matched_category: Optional[str] = None
    matched_keyword: Optional[str] = None

    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                matched_category = category
                matched_keyword = kw
                break
        if matched_category:
            break

    if matched_category is None:
        matched_category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Description does not clearly match any category in the allowed taxonomy."
    else:
        flag = ""
        reason = (
            f'Classified as {matched_category} based on '
            f'"{matched_keyword}" found in description.'
        )

    severity_trigger = find_severity_trigger(description)
    if severity_trigger:
        priority = "Urgent"
        reason += f' Priority set to Urgent due to severity keyword "{severity_trigger}".'
    elif matched_category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

    return {
        "category": matched_category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read all complaint rows from input_path, classify each one,
    and write enriched rows to output_path.
    """
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    rows_out = []
    with open(source, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        base_fields = list(reader.fieldnames or [])
        output_fields = base_fields + ["category", "priority", "reason", "flag"]

        for row in reader:
            complaint_id = row.get("complaint_id", "?")
            try:
                result = classify_complaint(row)
            except Exception as exc:
                print(
                    f"Warning: Could not classify row {complaint_id}: {exc}",
                    file=sys.stderr,
                )
                result = {
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Classification error — row skipped.",
                    "flag": "NEEDS_REVIEW",
                }
            rows_out.append({**row, **result})

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Classified {len(rows_out)} complaint(s) → {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0A Municipal Complaint Classifier"
    )
    parser.add_argument("--input",  required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()
    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
