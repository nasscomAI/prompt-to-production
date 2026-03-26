"""
UC-0A: Civic Complaint Classifier
Nasscom AI Code Sarathi — Prompt to Production

Reads test_hyderabad.csv, classifies each complaint by:
  - category    (Roads, Water, Sanitation, Electricity, Public Safety, Other)
  - severity    (High, Medium, Low)
  - priority    (1=highest … 3=lowest)

Outputs results_hyderabad.csv in the same directory.

Usage:
    python classifier.py
    python classifier.py --input data/city-test-files/test_hyderabad.csv
"""

import csv
import json
import re
import argparse
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CATEGORIES = [
    "Roads",
    "Water",
    "Sanitation",
    "Electricity",
    "Public Safety",
    "Other",
]

SEVERITY_LEVELS = ["High", "Medium", "Low"]

# Rule-based keyword maps (fast, zero-cost fallback / primary classifier)
CATEGORY_KEYWORDS = {
    "Roads": [
        "pothole", "road", "footpath", "pavement", "bridge", "signal",
        "traffic", "divider", "street", "highway", "crater", "broken road",
        "damaged road", "speed breaker",
    ],
    "Water": [
        "water", "pipe", "leak", "drainage", "flood", "sewage", "drain",
        "overflow", "waterlogging", "borewell", "supply", "tap", "pump",
    ],
    "Sanitation": [
        "garbage", "waste", "trash", "litter", "dustbin", "sweeping",
        "cleanliness", "toilet", "open defecation", "stench", "smell",
        "rubbish", "dump",
    ],
    "Electricity": [
        "electricity", "power", "light", "streetlight", "transformer",
        "wire", "electric", "outage", "voltage", "pole", "cable",
    ],
    "Public Safety": [
        "accident", "injury", "fire", "hospital", "school", "child",
        "crime", "theft", "harassment", "unsafe", "danger", "emergency",
        "dog bite", "stray", "violence",
    ],
}

# Severity triggers — presence of ANY of these bumps severity to High
HIGH_SEVERITY_KEYWORDS = [
    "injury", "injured", "dead", "death", "hospital", "child", "children",
    "school", "fire", "accident", "danger", "emergency", "unsafe", "kill",
    "flood", "collapse", "broken wire", "electric shock",
]

MEDIUM_SEVERITY_KEYWORDS = [
    "major", "severe", "urgent", "weeks", "months", "repeated", "again",
    "still", "no action", "ignored", "overflowing", "blocked",
]


# ---------------------------------------------------------------------------
# Classification logic
# ---------------------------------------------------------------------------

def classify_complaint(text: str) -> dict:
    """
    Classify a complaint text and return category, severity, priority.
    Uses keyword matching — deterministic, reproducible, no API needed.
    """
    text_lower = text.lower()

    # --- Category ---
    category_scores = {cat: 0 for cat in CATEGORIES}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                category_scores[cat] += 1

    best_cat = max(category_scores, key=category_scores.get)
    category = best_cat if category_scores[best_cat] > 0 else "Other"

    # --- Severity ---
    severity = "Low"  # default
    for kw in MEDIUM_SEVERITY_KEYWORDS:
        if kw in text_lower:
            severity = "Medium"
            break
    for kw in HIGH_SEVERITY_KEYWORDS:
        if kw in text_lower:
            severity = "High"
            break  # High overrides everything

    # --- Priority (1=High, 2=Medium, 3=Low) ---
    priority_map = {"High": 1, "Medium": 2, "Low": 3}
    priority = priority_map[severity]

    return {
        "category": category,
        "severity": severity,
        "priority": priority,
    }


# ---------------------------------------------------------------------------
# CSV I/O
# ---------------------------------------------------------------------------

def find_text_column(fieldnames: list) -> str:
    """
    Identify which column holds the complaint text.
    Checks common names in order of preference.
    """
    preferred = ["complaint", "description", "text", "complaint_text",
                 "issue", "details", "message", "content"]
    fieldnames_lower = {f.lower(): f for f in fieldnames}
    for p in preferred:
        if p in fieldnames_lower:
            return fieldnames_lower[p]
    # Fallback: return the last column (often the free-text field)
    return fieldnames[-1]


def process_csv(input_path: Path, output_path: Path) -> int:
    """
    Read input CSV, classify each row, write output CSV.
    Returns number of rows processed.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames or []

        text_col = find_text_column(fieldnames)
        print(f"  Using column '{text_col}' as complaint text source.")

        output_fields = fieldnames + ["category", "severity", "priority"]
        # Avoid duplicating columns if they already exist
        output_fields = list(dict.fromkeys(output_fields))

        rows_out = []
        count = 0
        for row in reader:
            complaint_text = row.get(text_col, "")
            result = classify_complaint(complaint_text)
            row["category"] = result["category"]
            row["severity"] = result["severity"]
            row["priority"] = result["priority"]
            rows_out.append(row)
            count += 1

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows_out)

    return count


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0A Civic Complaint Classifier"
    )
    parser.add_argument(
        "--input",
        default="data/city-test-files/test_hyderabad.csv",
        help="Path to input CSV (default: data/city-test-files/test_hyderabad.csv)",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Path to output CSV (default: results_<city>.csv next to input)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    # Derive output path from input filename if not specified
    if args.output:
        output_path = Path(args.output)
    else:
        city = input_path.stem.replace("test_", "")   # e.g. "hyderabad"
        output_path = input_path.parent / f"results_{city}.csv"

    print(f"UC-0A Complaint Classifier")
    print(f"  Input  : {input_path}")
    print(f"  Output : {output_path}")

    count = process_csv(input_path, output_path)

    print(f"  Done   : {count} complaints classified → {output_path}")


if __name__ == "__main__":
    main()
