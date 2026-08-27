"""
UC-0A — Complaint Classifier
Implements the two skills defined in skills.md under the enforcement rules
from agents.md.

Skills
------
  classify_complaint  — classifies one complaint row
  batch_classify      — reads input CSV, applies classify_complaint, writes output CSV

Run
---
  python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Agent configuration (sourced from agents.md)
# ---------------------------------------------------------------------------

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
    "hospitalised",
    "hospitalized",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

# Keyword → category mapping (order matters: first match wins for unambiguous hits)
# Use whole-phrase strings; matching is done via substring search on lowercased description.
CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Pothole",         ["pothole", "pot hole", "pot-hole"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlogged", "knee-deep", "submerged",
                         "water-logged", "at flooding risk"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "light out", "lights out",
                         "flickering", "sparking", "unlit", "no lighting", "area dark", "area very dark",
                         "darkness", "substation"]),
    ("Waste",           ["garbage", "rubbish", "litter", "refuse", "dead animal", "waste bin",
                         "waste not cleared", "waste overflow", "overflowing waste", "waste dump",
                         "bulk waste", "post-market waste", "market waste", "restaurant waste bins"]),
    ("Noise",           ["noise", "music", "loud", "sound", "midnight", "amplifier", "drilling"]),
    ("Road Damage",     ["road surface", "road collapsed", "road subsid", "cracked", "sinking",
                         "road damage", "manhole", "broken road", "buckled", "subsided", "subsidence",
                         "cobblestone", "tarmac", "surface melting", "paving removed", "footpath broken",
                         "footpath tiles"]),
    ("Heritage Damage", ["heritage", "historical", "monument", "old city", "historic tram",
                         "heritage stone", "heritage street", "heritage zone", "heritage area",
                         "heritage precinct", "heritage lamp", "heritage residential",
                         "ancient step well"]),
    ("Heat Hazard",     ["heatwave", "heat hazard", "dangerous temperature", "dangerous temperatures",
                         "surface temperature", "metal.*hot", "unbearable.*heat", "heat.*unbearable",
                         "storing heat", "52°c", "45°c", "44°c"]),
    ("Drain Blockage",  ["drain blocked", "drain block", "blocked drain", "drainage", "stormwater drain",
                         "drain completely", "main drain blocked"]),
]

AMBIGUOUS_REVIEW_THRESHOLD = 0.20  # 20 % ambiguous rows triggers a warning


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class ComplaintRow:
    description: str
    extra: dict = field(default_factory=dict)  # all other columns preserved


@dataclass
class ClassifiedRow:
    description: str
    category: str
    priority: str
    reason: str
    flag: str
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Skill 1 — classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: ComplaintRow) -> ClassifiedRow:
    """Classify one complaint row into category, priority, reason, and flag.

    Input:  ComplaintRow with description (required).
    Output: ClassifiedRow with {category, priority, reason, flag}.

    Error handling: If category is indeterminate, return category=Other,
    flag=NEEDS_REVIEW; still provide priority and reason from available
    description evidence.
    """
    description = row.description.strip()
    desc_lower = description.lower()

    # --- Priority: check severity keywords first (agents.md enforcement) ---
    triggered_severity = [
        kw for kw in SEVERITY_KEYWORDS
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower)
    ]
    priority = "Urgent" if triggered_severity else "Standard"

    # --- Category: keyword matching (supports plain substrings and regex patterns) ---
    matched_categories: list[tuple[str, list[str]]] = []  # (category, matched_words)
    for category, keywords in CATEGORY_KEYWORDS:
        hits = []
        for kw in keywords:
            try:
                if re.search(kw, desc_lower):
                    hits.append(kw)
            except re.error:
                if kw in desc_lower:
                    hits.append(kw)
        if hits:
            matched_categories.append((category, hits))

    flag = ""
    ambiguous_candidates: list[str] = []

    if len(matched_categories) == 1:
        category = matched_categories[0][0]
        evidence_words = matched_categories[0][1]
    elif len(matched_categories) > 1:
        # Multiple matches — pick highest-hit count; flag ties as NEEDS_REVIEW
        matched_categories.sort(key=lambda x: len(x[1]), reverse=True)
        if len(matched_categories[0][1]) == len(matched_categories[1][1]):
            # Tie → genuinely ambiguous
            category = "Other"
            flag = "NEEDS_REVIEW"
            evidence_words = matched_categories[0][1]
            ambiguous_candidates = [c for c, _ in matched_categories]
        else:
            category = matched_categories[0][0]
            evidence_words = matched_categories[0][1]
    else:
        # No keyword match
        category = "Other"
        flag = "NEEDS_REVIEW"
        evidence_words = []

    # --- Reason: must cite at least one specific word/phrase from description ---
    if ambiguous_candidates:
        cited = evidence_words[0]
        candidates_str = " and ".join(ambiguous_candidates[:2])
        reason = (
            f"Description contains '{cited}' but matches both {candidates_str}; "
            f"category is ambiguous and requires manual review."
        )
    elif evidence_words:
        cited = evidence_words[0]
        reason = f"Description contains '{cited}', indicating a {category} issue."
    elif triggered_severity:
        reason = (
            f"Description contains severity keyword '{triggered_severity[0]}'; "
            f"category could not be determined from description alone."
        )
    else:
        reason = "Description did not match any known category keywords; marked for manual review."

    return ClassifiedRow(
        description=description,
        category=category,
        priority=priority,
        reason=reason,
        flag=flag,
        extra=row.extra,
    )


# ---------------------------------------------------------------------------
# Skill 2 — batch_classify
# ---------------------------------------------------------------------------

REQUIRED_COLUMN = "description"
OUTPUT_COLUMNS = ["description", "category", "priority", "reason", "flag"]


def batch_classify(input_path: str, output_path: str) -> None:
    """Read input CSV, apply classify_complaint to each row, write output CSV.

    Input:  CSV file path containing complaint descriptions.
    Output: CSV with columns: description, category, priority, reason, flag.

    Error handling:
      - If the required 'description' column is missing, fail with a schema error.
      - If more than 20 % of rows are ambiguous (NEEDS_REVIEW), complete output
        and emit a warning for manual review.
    """
    src = Path(input_path)
    if not src.exists():
        sys.exit(f"[ERROR] Input file not found: {input_path}")

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or REQUIRED_COLUMN not in reader.fieldnames:
            sys.exit(
                f"[SCHEMA ERROR] Required column '{REQUIRED_COLUMN}' not found in "
                f"{input_path}. Available columns: {list(reader.fieldnames or [])}"
            )
        raw_rows = list(reader)

    if not raw_rows:
        print("[WARNING] Input file contains no data rows.")

    classified: list[ClassifiedRow] = []
    for raw in raw_rows:
        description = raw.get("description", "").strip()
        extra = {k: v for k, v in raw.items() if k != "description"}
        result = classify_complaint(ComplaintRow(description=description, extra=extra))
        classified.append(result)

    # --- Ambiguity check (agents.md: > 20 % NEEDS_REVIEW → warn) ---
    needs_review_count = sum(1 for r in classified if r.flag == "NEEDS_REVIEW")
    if classified and needs_review_count / len(classified) > AMBIGUOUS_REVIEW_THRESHOLD:
        print(
            f"[WARNING] {needs_review_count}/{len(classified)} rows ({needs_review_count/len(classified):.0%}) "
            f"are flagged NEEDS_REVIEW — exceeds 20% threshold. Manual review recommended."
        )

    # --- Write output CSV ---
    dest = Path(output_path)
    # Preserve all original columns except category/priority_flag (stripped per spec),
    # then append the four classification columns.
    original_cols = [c for c in (raw_rows[0].keys() if raw_rows else [])
                     if c not in ("description", "category", "priority_flag")]
    out_fieldnames = ["description"] + original_cols + ["category", "priority", "reason", "flag"]

    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fieldnames)
        writer.writeheader()
        for row in classified:
            out_row: dict = {"description": row.description}
            out_row.update(row.extra)
            out_row["category"] = row.category
            out_row["priority"] = row.priority
            out_row["reason"] = row.reason
            out_row["flag"] = row.flag
            writer.writerow(out_row)

    print(f"[OK] Classified {len(classified)} rows → {output_path}")
    if needs_review_count:
        print(f"     {needs_review_count} row(s) flagged NEEDS_REVIEW.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier — batch-classifies municipal complaints."
    )
    parser.add_argument("--input",  required=True, help="Path to input CSV file.")
    parser.add_argument("--output", required=True, help="Path to output CSV file.")
    args = parser.parse_args()
    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
