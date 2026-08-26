#!/usr/bin/env python3
"""
UC-0A — Complaint Classifier
Civic Tech Edition · Vibe Coding Workshop

Reads a city complaint CSV (category + priority_flag stripped) and classifies
each row against a FIXED schema. The enforcement rules below are the whole point
of the exercise: the naive prompt "classify by category and priority" drifts on
category names, goes blind to severity, and skips the reason field. This script
encodes the CRAFT enforcement so those failures cannot happen.

Run:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""

import argparse
import csv
import sys

# ─────────────────────────────────────────────────────────────────────────────
# ENFORCEMENT 1 — Fixed taxonomy. Exact strings only. No variations, no new
# categories invented at runtime (prevents Taxonomy drift + Hallucinated sub-cats)
# ─────────────────────────────────────────────────────────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Keyword -> category. Order matters: first matching category wins by priority.
# Each keyword list is checked against the lower-cased description.
CATEGORY_KEYWORDS = [
    ("Drain Blockage", ["drain blocked", "drain is blocked", "blocked drain", "manhole", "drain"]),
    ("Flooding",       ["flood", "flooded", "knee-deep", "waterlogg", "water logging", "standing in water", "submerged"]),
    ("Pothole",        ["pothole", "tyre damage", "tire damage"]),
    ("Road Damage",    ["road surface", "cracked", "sinking", "footpath", "tiles broken", "subsidence", "road damage", "upturned"]),
    ("Streetlight",    ["streetlight", "street light", "lights out", "light out", "lamp", "dark at night", "flickering", "sparking"]),
    ("Waste",          ["garbage", "waste", "dumped", "bins", "dead animal", "trash", "rubbish", "dumping"]),
    ("Noise",          ["music", "noise", "loud", "midnight"]),
    ("Heritage Damage",["heritage"]),
    ("Heat Hazard",    ["heat", "heatstroke", "shade", "temperature"]),
]

# ─────────────────────────────────────────────────────────────────────────────
# ENFORCEMENT 2 — Severity keywords MUST force priority = Urgent.
# This is the "severity blindness" fix: enforcement references these EXACT words.
# ─────────────────────────────────────────────────────────────────────────────
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Words that imply a category could be more than one thing -> NEEDS_REVIEW
AMBIGUITY_SIGNALS = [
    ("Drain Blockage", "Flooding"),   # blocked drain + flooding described together
]


def classify_complaint(row):
    """
    ENFORCEMENT 3 — one row in, full structured verdict out.
    Returns category, priority, reason (citing words), flag.
    Never returns a category outside ALLOWED_CATEGORIES.
    """
    desc = (row.get("description") or "").strip()
    low = desc.lower()

    # --- category ---
    matched = []
    category = "Other"
    for cat, kws in CATEGORY_KEYWORDS:
        hit = next((k for k in kws if k in low), None)
        if hit:
            matched.append((cat, hit))
    if matched:
        category = matched[0][0]
    if category not in ALLOWED_CATEGORIES:   # belt-and-suspenders guard
        category = "Other"

    # --- priority (severity enforcement) ---
    severity_hits = [w for w in SEVERITY_KEYWORDS if w in low]
    if severity_hits:
        priority = "Urgent"
    elif category == "Other":
        priority = "Low"
    else:
        priority = "Standard"

    # --- ambiguity flag ---
    matched_cats = {m[0] for m in matched}
    flag = ""
    for a, b in AMBIGUITY_SIGNALS:
        if a in matched_cats and b in matched_cats:
            flag = "NEEDS_REVIEW"
    if not matched:   # nothing matched at all -> genuinely ambiguous
        flag = "NEEDS_REVIEW"

    # --- reason (must cite specific words from the description) ---
    cited = []
    if matched:
        cited.append(f"'{matched[0][1]}'")
    if severity_hits:
        cited.append("severity term '" + severity_hits[0] + "'")
    if cited:
        reason = f"Classified as {category} ({priority}) because description contains " + " and ".join(cited) + "."
    else:
        reason = f"No clear category keyword found; defaulted to {category} and flagged for human review."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path, output_path):
    """ENFORCEMENT 4 — read CSV, classify each row, write CSV with new columns."""
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    for col in ["category", "priority", "reason", "flag"]:
        if col not in fieldnames:
            fieldnames.append(col)

    for row in rows:
        verdict = classify_complaint(row)
        row.update(verdict)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    urgent = sum(1 for r in rows if r["priority"] == "Urgent")
    review = sum(1 for r in rows if r["flag"] == "NEEDS_REVIEW")
    print(f"Classified {len(rows)} complaints -> {output_path}")
    print(f"  Urgent: {urgent}   NEEDS_REVIEW: {review}")
    for r in rows:
        print(f"  {r.get('complaint_id','?'):<12} {r['category']:<16} {r['priority']:<9} {r['flag']}")


def main():
    p = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    p.add_argument("--input", required=True, help="Path to test_[city].csv")
    p.add_argument("--output", required=True, help="Path to results_[city].csv")
    args = p.parse_args()
    try:
        batch_classify(args.input, args.output)
    except FileNotFoundError:
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
