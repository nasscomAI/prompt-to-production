"""
UC-0A — Complaint Classifier
Implemented according to agents.md (RICE) and skills.md.

Enforcement rules (from agents.md):
  1. Category must be exactly one of the 10 allowed values — no variations.
  2. Priority = Urgent if description contains any severity keyword (case-insensitive).
  3. Every output row must include a reason citing specific words from the description.
  4. If category cannot be determined → category: Other, flag: NEEDS_REVIEW.
  5. Category names must never vary across rows for the same complaint type.

Context boundary (from agents.md):
  Only the 'description' field may influence classification.
  complaint_id, city, ward, date, location, reported_by, days_open are passed through
  unchanged and must NOT influence category, priority, reason, or flag.
"""

import argparse
import csv
import re

# ── Taxonomy (enforcement rule 1) ─────────────────────────────────────────────
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

# ── Severity keywords → Urgent (enforcement rule 2) ───────────────────────────
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ── Category keyword map ───────────────────────────────────────────────────────
# Each entry: (category_name, [list of trigger words/phrases])
# Checked in order; first match wins. 'Other' is the fallback.
# Drain Blockage checked before Flooding to catch "drain blocked" specifically.
CATEGORY_RULES = [
    # Drain Blockage before Flooding — catches "drain blocked" / "drain overflow" first
    ("Drain Blockage",  ["drain block", "drain clog", "drain overflow", "blocked drain",
                         "clogged drain", "drain choke"]),
    # Waste before Flooding — catches "overflowing garbage/bins" before generic "overflow"
    ("Waste",           ["garbage", "waste", "rubbish", "litter", "trash",
                         "overflowing bin", "overflowing garbage", "bin overflow",
                         "dump", "sanitation", "refuse", "debris"]),
    ("Flooding",        ["flood", "waterlog", "water-log", "inundat", "submerge",
                         "knee-deep", "standing water", "overflow"]),
    ("Pothole",         ["pothole", "pot hole", "tyre damage", "road crater"]),
    ("Road Damage",     ["road damage", "road crack", "road broken", "road collapse",
                         "damaged road", "road surface", "road deteriorat",
                         "road cave", "road sink", "road subsid"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "light out",
                         "light not work", "light broken", "dark street",
                         "no light", "light off"]),
    ("Noise",           ["noise", "loud", "sound", "music", "horn", "blaring",
                         "disturbance", "nuisance"]),
    ("Heritage Damage", ["heritage", "monument", "historic", "ancient", "temple",
                         "fort", "archaeological", "heritage site"]),
    ("Heat Hazard",     ["heat", "heatwave", "heat wave", "hot", "temperature",
                         "heat stroke", "heat exhaustion", "sun stroke"]),
]

OUTPUT_FIELDNAMES = [
    "complaint_id", "date_raised", "city", "ward", "location",
    "description", "reported_by", "days_open",
    "category", "priority", "reason", "flag",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _check_urgent(description: str) -> tuple[bool, str]:
    """Return (is_urgent, matched_keyword). Case-insensitive."""
    desc_lower = description.lower()
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            return True, kw
    return False, ""


def _match_category(description: str) -> tuple[str, str | None]:
    """
    Return (category, matched_phrase_or_None).
    Tries each rule in order; returns ('Other', None) if nothing matches.
    """
    desc_lower = description.lower()
    for category, triggers in CATEGORY_RULES:
        for trigger in triggers:
            if trigger in desc_lower:
                return category, trigger
    return "Other", None


def _build_reason(description: str, category: str, matched_phrase: str | None,
                  is_urgent: bool, urgent_keyword: str) -> str:
    """
    Build a one-sentence reason citing specific words from the description.
    Enforcement rule 3: must cite specific words from the input.
    """
    parts = []

    if matched_phrase:
        # Find the actual casing from the description
        pattern = re.compile(re.escape(matched_phrase), re.IGNORECASE)
        m = pattern.search(description)
        cited_phrase = m.group(0) if m else matched_phrase
        parts.append(f'description contains "{cited_phrase}" → classified as {category}')
    else:
        parts.append(f"description does not match any known category → classified as Other")

    if is_urgent:
        pattern = re.compile(re.escape(urgent_keyword), re.IGNORECASE)
        m = pattern.search(description)
        cited_kw = m.group(0) if m else urgent_keyword
        parts.append(f'severity keyword "{cited_kw}" triggers Urgent priority')

    return "; ".join(parts) + "."


# ── Skill: classify_complaint ─────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input:  dict — must contain 'description'; all other keys passed through unchanged.
    Output: dict — original keys preserved, four fields added:
              category · priority · reason · flag

    Context boundary: only 'description' influences classification (agents.md).
    """
    result = dict(row)  # pass-through all original columns unchanged

    description = (row.get("description") or "").strip()

    # ── Empty / missing description ───────────────────────────────────────────
    if not description:
        result["category"] = "Other"
        result["priority"] = "Low"
        result["reason"]   = "No description provided."
        result["flag"]     = "NEEDS_REVIEW"
        return result

    # ── Category match (enforcement rules 1, 4, 5) ───────────────────────────
    category, matched_phrase = _match_category(description)

    # ── Priority (enforcement rule 2) ─────────────────────────────────────────
    is_urgent, urgent_keyword = _check_urgent(description)
    priority = "Urgent" if is_urgent else "Standard"

    # Low priority: short descriptions with no strong category signal and no urgency
    if category == "Other" and not is_urgent:
        priority = "Low"

    # ── Flag (enforcement rule 4) ─────────────────────────────────────────────
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    # ── Reason (enforcement rule 3) ───────────────────────────────────────────
    reason = _build_reason(description, category, matched_phrase, is_urgent, urgent_keyword)

    result["category"] = category
    result["priority"] = priority
    result["reason"]   = reason
    result["flag"]     = flag
    return result


# ── Skill: batch_classify ─────────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.

    - Raises FileNotFoundError if input_path does not exist.
    - Raises ValueError if 'description' column is missing.
    - On per-row failure: writes category=Other, flag=NEEDS_REVIEW, reason=error message.
      Does NOT abort the batch.
    - Prints summary to stdout: total · Urgent count · NEEDS_REVIEW count.
    """
    # ── Read ──────────────────────────────────────────────────────────────────
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"Input file '{input_path}' appears to be empty.")
            fieldnames = list(reader.fieldnames)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if "description" not in fieldnames:
        raise ValueError(
            f"Required column 'description' not found in '{input_path}'. "
            f"Columns present: {fieldnames}"
        )

    # ── Classify ──────────────────────────────────────────────────────────────
    results = []
    urgent_count      = 0
    needs_review_count = 0

    for row in rows:
        try:
            classified = classify_complaint(row)
        except Exception as exc:  # row-level isolation — do not abort batch
            classified = dict(row)
            classified["category"] = "Other"
            classified["priority"] = "Low"
            classified["reason"]   = f"Classification error: {exc}"
            classified["flag"]     = "NEEDS_REVIEW"

        if classified.get("priority") == "Urgent":
            urgent_count += 1
        if classified.get("flag") == "NEEDS_REVIEW":
            needs_review_count += 1

        results.append(classified)

    # ── Write ─────────────────────────────────────────────────────────────────
    # Build output fieldnames: original columns + classification fields (no duplicates)
    classification_fields = ["category", "priority", "reason", "flag"]
    out_fieldnames = [f for f in fieldnames if f not in classification_fields] + classification_fields

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    # ── Summary ───────────────────────────────────────────────────────────────
    total = len(results)
    print(f"\n── UC-0A Batch Classification Summary ──────────────────")
    print(f"  Input            : {input_path}")
    print(f"  Output           : {output_path}")
    print(f"  Total rows       : {total}")
    print(f"  Urgent           : {urgent_count}")
    print(f"  NEEDS_REVIEW     : {needs_review_count}")
    print(f"  Standard/Low     : {total - urgent_count - needs_review_count}")
    print(f"────────────────────────────────────────────────────────\n")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier — RICE-enforced taxonomy classifier"
    )
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results_[city].csv")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
