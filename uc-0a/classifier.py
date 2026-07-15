"""
UC-0A — Complaint Classifier
Implements RICE enforcement rules from agents.md and skill contracts from skills.md.

Run:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""

import argparse
import csv
import re
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Schema — single source of truth for enforcement
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
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword → category mapping (ordered: more specific rules first)
# Each entry: (list_of_trigger_words, category)
# The FIRST match wins.
CATEGORY_RULES = [
    # Heritage Damage — check before Road Damage (heritage streets, zones exist)
    (["heritage", "monument", "historical", "ancient", "heritage street",
      "heritage zone", "old city", "charminar"], "Heritage Damage"),
    # Drain Blockage — explicit drain/sewer block including stormwater, drainage onto road
    (["drain blocked", "drain block", "blocked drain", "sewer block", "blocked sewer",
      "drain overflow", "drain choked", "stormwater drain", "storm water drain",
      "main drain", "drain 100%", "drain completely", "mosquito breeding",
      "clogged drain", "draining directly", "draining onto"], "Drain Blockage"),
    # Flooding — standing water, flood, inundated, waterlogged, rainwater channelling
    (["flood", "flooded", "inundated", "waterlogged", "water logging",
      "submerged", "knee-deep", "standing water", "flooding risk",
      "channel rainwater", "rainwater", "filling with rainwater"], "Flooding"),
    # Pothole — pothole keyword directly
    (["pothole", "pot hole", "pot-hole"], "Pothole"),
    # Road Damage — cracked, sinking, broken road, manhole, footpath, collapse, crater,
    #              buckled, subsided, cobblestones broken, paving removed
    (["road surface", "road crack", "cracked road", "sinking", "manhole",
      "footpath", "road damage", "road broken", "tiles broken", "upturned",
      "road deteriorat", "road collapsed", "collapsed", "crater", "road cave",
      "pavement", "buckled", "subsided", "cobblestone", "cobble stone",
      "paving removed", "stone not replaced", "road subsid", "structural concern",
      "tram road"], "Road Damage"),
    # Streetlight — light out, streetlight, sparking light, substation, unlit
    (["streetlight", "street light", "street-light", "lights out",
      "light out", "flickering", "sparking", "lamp", "darkness",
      "substation", "no power", "power outage", "unlit", "wiring theft"], "Streetlight"),
    # Waste — garbage, waste, dumping, litter, dead animal, overflow
    (["garbage", "waste", "trash", "litter", "dumping", "dump", "dead animal",
      "refuse", "overflowing bin", "overflowing garbage", "bin overflow",
      "post-market waste", "not cleared", "waste overflowing", "piles"], "Waste"),
    # Noise — noise, music, sound, loud, drilling, idling engines, amplifiers
    (["noise", "music", "sound", "loud", "midnight", "nighttime",
      "drilling", "idling", "engines on", "engine on",
      "amplifier", "band playing", "wedding band"], "Noise"),
    # Heat Hazard — heat, temperature, heat wave, tarmac melting, surface temperature
    (["heat", "temperature", "heat wave", "heatwave", "hot",
      "tarmac", "melting", "surface temperature", "storing heat", "burns on contact"], "Heat Hazard"),
]


# ---------------------------------------------------------------------------
# Skill 1 — classify_complaint
# ---------------------------------------------------------------------------

def _check_severity(description: str) -> bool:
    """Return True if any severity keyword appears in the description (case-insensitive)."""
    desc_lower = description.lower()
    return any(kw in desc_lower for kw in SEVERITY_KEYWORDS)


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Determine category from description using keyword rules.
    Returns (category, is_ambiguous).
    """
    desc_lower = description.lower()

    matched_categories = []
    for trigger_words, category in CATEGORY_RULES:
        if any(tw in desc_lower for tw in trigger_words):
            matched_categories.append(category)

    if len(matched_categories) == 0:
        return "Other", True          # Nothing matched → genuinely ambiguous
    if len(matched_categories) == 1:
        return matched_categories[0], False
    # Multiple matches — pick the first/most specific one but flag for review
    # unless all matches are the same category
    unique = list(dict.fromkeys(matched_categories))  # preserve order, deduplicate
    if len(unique) == 1:
        return unique[0], False
    return unique[0], True            # Multiple distinct categories → flag


def _build_reason(description: str, category: str) -> str:
    """
    Build a one-sentence reason that cites specific words from the description.
    """
    # Find the most informative phrase in description to quote
    # Strategy: pull the first sentence or up to 80 chars, quoting key words.
    desc = description.strip()
    # Extract a short representative snippet (first sentence or ≤80 chars)
    sentences = re.split(r'(?<=[.!?])\s+', desc)
    snippet = sentences[0] if sentences else desc
    if len(snippet) > 90:
        snippet = snippet[:87] + "..."

    return f'Classified as {category} based on description: "{snippet}"'


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input:
        row — dict with at minimum: complaint_id, description
    Returns:
        dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # --- Handle missing/empty description (enforcement rule 6) ---
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description field is missing or empty — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    # --- Determine category ---
    category, is_ambiguous = _detect_category(description)

    # --- Determine priority (enforcement rule 2) ---
    if _check_severity(description):
        priority = "Urgent"
    elif category == "Noise":
        # Noise without safety element → Low
        priority = "Low"
    else:
        priority = "Standard"

    # --- Build reason (enforcement rule 3) ---
    reason = _build_reason(description, category)

    # --- Set flag (enforcement rule 4) ---
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Skill 2 — batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.

    Enforcement:
    - Never crashes on a single bad row; bad rows get Other + NEEDS_REVIEW.
    - Prints a summary after processing.
    """
    # --- Validate input file ---
    try:
        with open(input_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise ValueError(f"Input file '{input_path}' appears to be empty.")
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Could not read input file '{input_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print(f"WARNING: No data rows found in '{input_path}'.")
        return

    # --- Process each row ---
    output_rows = []
    error_rows = []
    urgent_count = 0
    needs_review_count = 0

    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as exc:
            # Safety net — should never fire, but never let one row kill the batch
            result = {
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Unexpected classification error: {exc}",
                "flag": "NEEDS_REVIEW",
            }
            error_rows.append(result["complaint_id"])

        if result["priority"] == "Urgent":
            urgent_count += 1
        if result["flag"] == "NEEDS_REVIEW":
            needs_review_count += 1

        # Merge original row fields with classification fields
        merged = dict(row)
        merged.update(result)
        output_rows.append(merged)

    # --- Write output CSV ---
    # Output fieldnames: all original columns + classification columns (if not already present)
    original_fields = list(rows[0].keys()) if rows else []
    classification_fields = ["category", "priority", "reason", "flag"]
    # Avoid duplicating fields that might already exist in input
    extra_fields = [f for f in classification_fields if f not in original_fields]
    output_fields = original_fields + extra_fields

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=output_fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(output_rows)
    except Exception as exc:
        print(f"ERROR: Could not write output file '{output_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Summary report ---
    total = len(output_rows)
    print(f"\n{'='*55}")
    print(f"UC-0A Classification Complete")
    print(f"{'='*55}")
    print(f"  Input file   : {input_path}")
    print(f"  Output file  : {output_path}")
    print(f"  Total rows   : {total}")
    print(f"  Urgent       : {urgent_count}")
    print(f"  NEEDS_REVIEW : {needs_review_count}")
    if error_rows:
        print(f"  Row errors   : {len(error_rows)} — IDs: {', '.join(error_rows)}")
    print(f"{'='*55}\n")

    # --- Per-row quick view ---
    print(f"{'ID':<14} {'Category':<18} {'Priority':<10} {'Flag'}")
    print("-" * 58)
    for r in output_rows:
        print(
            f"{r['complaint_id']:<14} "
            f"{r['category']:<18} "
            f"{r['priority']:<10} "
            f"{r.get('flag','')}"
        )
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Civic Complaint Classifier — RICE-enforced"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to test_[city].csv",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV",
    )
    args = parser.parse_args()
    batch_classify(args.input, args.output)
