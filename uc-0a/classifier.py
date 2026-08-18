"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Agent Role (agents.md):
  Expert municipal complaint classification agent. Classifies complaint text
  into predefined structured fields without initiating any external actions.

Skills (skills.md):
  - classify_complaint: one complaint row in → category + priority + reason + flag out
  - batch_classify: reads input CSV, applies classify_complaint per row, writes output CSV

Enforcement (agents.md / README.md):
  - Category must be exactly one of the allowed list — no variations.
  - Priority must be Urgent if severity keywords present; otherwise Standard or Low.
  - Every row must include a reason citing specific words from the description.
  - Genuinely ambiguous items: category=Other, flag=NEEDS_REVIEW.
"""

import argparse
import csv
import re
import sys
from typing import Optional

# ── Schema constants ────────────────────────────────────────────────────────────

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

# Severity keywords that MUST trigger Urgent priority (agents.md enforcement)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword mapping — ordered by specificity (most specific first)
# Each entry: (category_name, list_of_trigger_words)
CATEGORY_RULES = [
    ("Heritage Damage",  ["heritage", "monument", "historical", "charminar", "old city", "fort", "temple", "archaeological"]),
    ("Heat Hazard",      ["heat", "temperature", "sunstroke", "thermal", "hot"]),
    ("Drain Blockage",   ["drain blocked", "drain blockage", "drain 100%", "drain completely", "stormwater drain", "drain block", "mosquito breeding", "drain—", "drain -"]),
    ("Flooding",         ["flood", "flooded", "flooding", "waterlog", "water-log", "inundated", "submerged", "rainwater"]),
    ("Pothole",          ["pothole", "pot hole", "crater", "potholes"]),
    ("Road Damage",      ["road collapsed", "road collapse", "collapse", "road caved", "road damage", "cave-in", "sinkhole", "pavement broken", "road broken"]),
    ("Streetlight",      ["streetlight", "street light", "lamp post", "lighting", "light out", "dark road", "no light"]),
    ("Waste",            ["garbage", "waste", "trash", "litter", "rubbish", "debris", "dumping", "solid waste", "post-market waste"]),
    ("Noise",            ["noise", "drilling", "loud", "construction noise", "sound", "blaring", "idling", "engine on", "trucks idling"]),
]


# ── Skill: classify_complaint ────────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint (skills.md)
    Classifies a single citizen complaint description into predefined constraint fields.

    Input:  A dict representing a single complaint row (must contain 'description'
            and 'complaint_id').
    Output: A dict with keys: complaint_id, category, priority, reason, flag.

    Error handling (skills.md):
      - Empty / incomprehensible input → category='Other', priority='Low',
        flag='NEEDS_REVIEW'
      - Ambiguous → category='Other', flag='NEEDS_REVIEW'
    """
    complaint_id  = row.get("complaint_id", "UNKNOWN").strip()
    description   = row.get("description", "").strip()

    # ── Handle empty / incomprehensible input ──────────────────────────────────
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "No description provided; cannot classify.",
            "flag":         "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Step 1: Determine priority (agents.md enforcement rule 2) ──────────────
    triggered_keyword = None
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            triggered_keyword = kw
            break

    priority = "Urgent" if triggered_keyword else _infer_base_priority(desc_lower)

    # ── Step 2: Determine category (agents.md enforcement rule 1) ──────────────
    matched_category = None
    matched_trigger  = None

    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                matched_category = category
                matched_trigger  = kw
                break
        if matched_category:
            break

    # ── Step 3: Resolve ambiguity (agents.md enforcement rule 4) ──────────────
    flag = ""
    if matched_category is None:
        # Could not confidently determine category from description alone
        matched_category = "Other"
        flag = "NEEDS_REVIEW"

    # ── Step 4: Build reason citing specific words (agents.md enforcement rule 3)
    reason = _build_reason(description, matched_category, priority,
                           matched_trigger, triggered_keyword)

    return {
        "complaint_id": complaint_id,
        "category":     matched_category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


def _infer_base_priority(desc_lower: str) -> str:
    """
    Infer Standard vs Low when no severity keyword is present.
    Standard: complaint mentions active disruption or ongoing failure.
    Low: complaint describes minor inconvenience or non-critical issue.
    """
    standard_signals = [
        "blocked", "collapsed", "flooded", "flood", "overflow", "unusable",
        "abandoned", "divert", "diverted", "hospitalised", "hospitalized",
        "losses", "risk", "struggling", "completely",
    ]
    for signal in standard_signals:
        if signal in desc_lower:
            return "Standard"
    return "Low"


def _build_reason(description: str, category: str, priority: str,
                  category_trigger: Optional[str], severity_trigger: Optional[str]) -> str:
    """
    Build a single-sentence reason that cites specific words from the description.
    (agents.md enforcement rule 3)
    """
    parts = []

    if category_trigger:
        # Find the actual casing from the description for the citation
        idx = description.lower().find(category_trigger)
        cited_phrase = description[idx: idx + len(category_trigger)] if idx != -1 else category_trigger
        parts.append(f'Classified as {category} due to "{cited_phrase}" in the description')
    else:
        parts.append(f"Classified as {category} as no specific category keyword was found")

    if severity_trigger:
        idx = description.lower().find(severity_trigger)
        cited_word = description[idx: idx + len(severity_trigger)] if idx != -1 else severity_trigger
        parts.append(f'priority set to Urgent because the description contains "{cited_word}"')
    else:
        parts.append(f"priority set to {priority} based on the described impact")

    return "; ".join(parts) + "."


# ── Skill: batch_classify ────────────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Skill: batch_classify (skills.md)
    Reads input CSV, applies classify_complaint per row, writes output CSV.

    Error handling (skills.md):
      - If a row fails to process: log the error, default to Other / NEEDS_REVIEW,
        continue remaining rows.
      - If input file is unreadable: halt with a file access error.
    """
    # ── Read input CSV ─────────────────────────────────────────────────────────
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames or []
    except (FileNotFoundError, PermissionError, OSError) as exc:
        # File access error — halt as per skills.md error handling
        print(f"[ERROR] Cannot read input file '{input_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Classify each row ──────────────────────────────────────────────────────
    output_rows = []
    for i, row in enumerate(rows, start=1):
        try:
            result = classify_complaint(row)
        except Exception as exc:
            # Per skills.md: log error, default to Other / NEEDS_REVIEW, continue
            complaint_id = row.get("complaint_id", f"row-{i}")
            print(f"[WARNING] Row {i} (id={complaint_id}) failed: {exc} — defaulting to Other/NEEDS_REVIEW",
                  file=sys.stderr)
            result = {
                "complaint_id": complaint_id,
                "category":     "Other",
                "priority":     "Low",
                "reason":       f"Processing error on row {i}; defaulted.",
                "flag":         "NEEDS_REVIEW",
            }

        # Merge original row fields with classification output
        merged = dict(row)
        merged["category"]  = result["category"]
        merged["priority"]  = result["priority"]
        merged["reason"]    = result["reason"]
        merged["flag"]      = result["flag"]
        output_rows.append(merged)

    # ── Write output CSV ───────────────────────────────────────────────────────
    if not output_rows:
        print("[WARNING] No rows to write.", file=sys.stderr)
        return

    # Output fieldnames = original columns + new classification columns
    new_fields = ["category", "priority", "reason", "flag"]
    out_fieldnames = list(fieldnames) + [f for f in new_fields if f not in fieldnames]

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(output_rows)
    except (PermissionError, OSError) as exc:
        print(f"[ERROR] Cannot write output file '{output_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Classified {len(output_rows)} complaints → {output_path}")


# ── Entry point ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
