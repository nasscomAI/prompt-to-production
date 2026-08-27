"""
UC-0A — Complaint Classifier
RICE-enforced deterministic classifier.
Fixes all 5 failure modes:
  1. Taxonomy drift         → Fixed enum, keyword-matched categories
  2. Severity blindness     → Explicit URGENT_KEYWORDS lookup
  3. Missing justification  → reason field always populated, cites description
  4. Hallucinated sub-cats  → Only allowed categories, Others + NEEDS_REVIEW on ambiguity
  5. False confidence       → Ambiguity detector sets flag=NEEDS_REVIEW
"""

import argparse
import csv
import re
import sys

# ── ENFORCEMENT: Fixed enum — no variations allowed ──────────────────────────
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

# ── ENFORCEMENT: Keywords that MUST trigger Urgent priority ──────────────────
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ── ENFORCEMENT: Category keyword mapping (order matters — first match wins) ─
CATEGORY_RULES = [
    # (category,         list of trigger keywords/phrases)
    ("Pothole",         ["pothole", "potholes", "pot-hole"]),
    ("Flooding",        ["flood", "flooded", "flooding", "water logging", "waterlog",
                         "knee-deep", "submerged", "water-logged"]),
    ("Streetlight",     ["streetlight", "street light", "light out", "lights out",
                         "lamp", "lighting", "sparking", "flickering"]),
    ("Waste",           ["garbage", "waste", "bin", "litter", "rubbish", "dump",
                         "dumped", "overflowing", "dead animal", "carcass"]),
    ("Noise",           ["noise", "music", "loud", "sound", "midnight", "wedding",
                         "DJ", "speaker"]),
    ("Road Damage",     ["road surface", "cracked", "sinking", "road damage",
                         "broken road", "manhole", "missing cover", "footpath",
                         "tiles broken", "upturned"]),
    ("Heritage Damage", ["heritage", "historic", "monument", "old building",
                         "heritage street"]),
    ("Drain Blockage",  ["drain", "blocked drain", "drain block", "sewer",
                         "drainage"]),
    ("Heat Hazard",     ["heat", "heatwave", "heat hazard", "extreme heat"]),
]

# ── ENFORCEMENT: Ambiguous signals — trigger NEEDS_REVIEW ───────────────────
AMBIGUOUS_SIGNALS = [
    ("Pothole",     "Flooding"),    # e.g. waterlogged pothole
    ("Waste",       "Road Damage"), # bulk waste on road — could be either
    ("Streetlight", "Heritage Damage"),  # heritage street with lights out
]


def _lower(text: str) -> str:
    return text.lower()


def _check_urgent(description: str) -> bool:
    """Return True if any URGENT_KEYWORDS are present (case-insensitive)."""
    desc_lower = _lower(description)
    return any(kw in desc_lower for kw in URGENT_KEYWORDS)


def _detect_category(description: str) -> tuple[str, str]:
    """
    Match description against CATEGORY_RULES.
    Returns (category, flag).
    If ambiguous (two categories match), returns ('Other', 'NEEDS_REVIEW').
    If no match, returns ('Other', 'NEEDS_REVIEW').
    """
    desc_lower = _lower(description)
    matched = []

    for category, keywords in CATEGORY_RULES:
        if any(kw in desc_lower for kw in keywords):
            matched.append(category)

    if len(matched) == 0:
        return "Other", "NEEDS_REVIEW"

    if len(matched) == 1:
        return matched[0], ""

    # Multiple categories matched — check if this is a known ambiguous pair
    # If so, flag it. Otherwise take the first (highest priority) match.
    matched_set = set(matched)
    for a, b in AMBIGUOUS_SIGNALS:
        if a in matched_set and b in matched_set:
            return "Other", "NEEDS_REVIEW"

    # Non-ambiguous multi-match: first rule wins (most specific)
    return matched[0], ""


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Build a one-sentence reason that cites specific words from the description.
    ENFORCEMENT: reason must reference actual words from the input.
    """
    # Find the matched urgent keyword if any
    urgent_kw = next(
        (kw for kw in URGENT_KEYWORDS if kw in _lower(description)), None
    )

    # Extract a short phrase from description (first 80 chars, trimmed at word boundary)
    excerpt = description.strip()
    if len(excerpt) > 80:
        excerpt = excerpt[:80].rsplit(" ", 1)[0] + "..."

    if priority == "Urgent" and urgent_kw:
        return (
            f"Classified as {category} and marked Urgent because description "
            f"contains '{urgent_kw}': \"{excerpt}\""
        )
    else:
        return (
            f"Classified as {category} based on description: \"{excerpt}\""
        )


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    RICE enforcement:
      - Category must be from ALLOWED_CATEGORIES (fixed enum)
      - Priority must be Urgent if URGENT_KEYWORDS present
      - Reason must cite specific words from description
      - Flag must be NEEDS_REVIEW on ambiguous inputs
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # ── ENFORCEMENT: handle missing/empty description ────────────────────────
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "No description provided — cannot classify.",
            "flag":         "NEEDS_REVIEW",
        }

    # ── ENFORCEMENT: Determine category (fixed enum, no hallucinations) ──────
    category, flag = _detect_category(description)

    # ── ENFORCEMENT: Priority driven by URGENT_KEYWORDS, not by AI guess ─────
    if _check_urgent(description):
        priority = "Urgent"
    else:
        priority = "Standard"

    # ── ENFORCEMENT: reason must cite description words ───────────────────────
    reason = _build_reason(description, category, priority)

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    - Flags nulls: rows with missing fields get NEEDS_REVIEW
    - Does not crash on bad rows: errors are caught per-row
    - Produces output even if some rows fail
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file not found: {input_path}. "
            "Ensure the path points to a valid city CSV file."
        )

    output_rows = []
    errors = 0

    for i, row in enumerate(rows, start=1):
        try:
            result = classify_complaint(row)
            # Merge original row with classification result
            combined = {**row, **result}
            output_rows.append(combined)
        except Exception as exc:
            # ── ENFORCEMENT: never crash the whole batch ──────────────────────
            complaint_id = row.get("complaint_id", f"ROW_{i}")
            combined = {
                **row,
                "complaint_id": complaint_id,
                "category":     "Other",
                "priority":     "Low",
                "reason":       f"Row classification error: {exc}",
                "flag":         "NEEDS_REVIEW",
            }
            output_rows.append(combined)
            errors += 1

    if not output_rows:
        print("Warning: No rows to classify.", file=sys.stderr)
        return

    # Determine fieldnames: original columns + classification columns (no duplicates)
    original_fields = list(rows[0].keys()) if rows else []
    extra_fields = ["category", "priority", "reason", "flag"]
    fieldnames = original_fields + [f for f in extra_fields if f not in original_fields]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)

    total = len(output_rows)
    urgent = sum(1 for r in output_rows if r.get("priority") == "Urgent")
    flagged = sum(1 for r in output_rows if r.get("flag") == "NEEDS_REVIEW")
    print(f"Classified {total} complaints — {urgent} Urgent, {flagged} flagged NEEDS_REVIEW, {errors} row errors.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
