"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify as defined in agents.md and skills.md.

Agent role    : Municipal citizen complaint classifier (classification & prioritisation only).
Input columns : complaint_id, date_raised, city, ward, location, description,
                reported_by, days_open
Output columns: (all above) + category, priority, reason, flag
"""
import argparse
import csv
import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.WARNING,
                    format="%(levelname)s: %(message)s")

# ---------------------------------------------------------------------------
# Enforcement constants  (agents.md → enforcement / skills.md → classification_schema)
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Priority override: any of these words (case-insensitive) → Urgent
URGENCY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword → category mapping (order matters; first match wins unless conflicting)
CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Pothole",        ["pothole", "pot hole", "crater", "pit in road", "pit on road"]),
    ("Flooding",       ["flood", "flooding", "waterlog", "water logging", "submerged", "inundated"]),
    ("Streetlight",    ["streetlight", "street light", "lamp post", "lamppost", "light out", "dark street", "no light"]),
    ("Waste",          ["garbage", "waste", "rubbish", "litter", "trash", "dumping", "bin overflow", "overflowing bin"]),
    ("Noise",          ["noise", "loud", "sound", "music", "horn", "blaring", "disturbance"]),
    ("Road Damage",    ["road damage", "damaged road", "broken road", "crack", "subsidence", "sinkhole", "road broken"]),
    ("Heritage Damage",["heritage", "monument", "historical", "ancient", "landmark", "heritage site"]),
    ("Heat Hazard",    ["heat", "hot surface", "burning", "temperature", "heat wave", "heatwave", "tar melting"]),
    ("Drain Blockage", ["drain", "blocked drain", "sewer", "clogged", "overflow drain", "manhole"]),
]

INPUT_COLUMNS = [
    "complaint_id", "date_raised", "city", "ward",
    "location", "description", "reported_by", "days_open",
]

OUTPUT_COLUMNS = INPUT_COLUMNS + ["category", "priority", "reason", "flag"]


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _find_urgency_matches(description: str) -> list[str]:
    """Return urgency keywords found in description (case-insensitive)."""
    lower = description.lower()
    return [kw for kw in URGENCY_KEYWORDS if kw in lower]


def _find_category(description: str) -> tuple[str, list[str], bool]:
    """
    Match description against CATEGORY_KEYWORDS.

    Returns:
        category  (str)       — one of ALLOWED_CATEGORIES
        matched   (list[str]) — the keyword(s) that triggered the match
        needs_review (bool)   — True when ambiguous / conflicting
    """
    lower = description.lower()
    matches: list[tuple[str, str]] = []   # (category, triggering_keyword)

    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in lower:
                matches.append((category, kw))
                break  # one match per category is enough

    # Deduplicate to unique categories
    unique_cats = list(dict.fromkeys(c for c, _ in matches))

    if len(unique_cats) == 0:
        return "Other", [], True          # cannot determine → NEEDS_REVIEW
    if len(unique_cats) == 1:
        triggering_kw = [kw for c, kw in matches if c == unique_cats[0]]
        return unique_cats[0], triggering_kw, False
    # Multiple conflicting categories
    triggering_kws = [kw for _, kw in matches]
    return "Other", triggering_kws, True  # conflicting → NEEDS_REVIEW


def _build_reason(description: str, category: str, urgency_matches: list[str],
                  category_keywords: list[str]) -> str:
    """
    Construct a one-sentence reason citing specific words from the description.
    agents.md enforcement: reason must cite specific words from the description.
    """
    parts: list[str] = []
    if category_keywords:
        parts.append(f"description contains '{', '.join(category_keywords)}' → category '{category}'")
    else:
        parts.append(f"no specific category keyword found → category 'Other'")
    if urgency_matches:
        parts.append(f"urgency keyword(s) '{', '.join(urgency_matches)}' detected → priority 'Urgent'")
    return "; ".join(parts).capitalize() + "."


# ---------------------------------------------------------------------------
# Core skill: classify_complaint  (skills.md → classify_complaint)
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input : dict with at minimum a 'description' key plus any of the
            INPUT_COLUMNS defined in agents.md.
    Output: dict with keys — complaint_id, category, priority, reason, flag.

    Enforcement (agents.md):
      - category ∈ ALLOWED_CATEGORIES (exact strings)
      - priority = 'Urgent' if any URGENCY_KEYWORDS present in description
      - reason must cite specific words from the description
      - ambiguous / conflicting category → 'Other' + flag 'NEEDS_REVIEW'
      - null / empty description → 'Other', 'Low', flag 'NEEDS_REVIEW'
    """
    complaint_id = row.get("complaint_id", "")
    description  = row.get("description", "") or ""

    # --- Guard: null / empty description (skills.md → error_handling) ---
    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description is null or empty; cannot classify.",
            "flag":         "NEEDS_REVIEW",
        }

    # --- Category ---
    category, cat_keywords, needs_review = _find_category(description)

    # --- Priority ---
    urgency_matches = _find_urgency_matches(description)
    if urgency_matches:
        priority = "Urgent"
    elif needs_review or category == "Other":
        priority = "Low"
    else:
        priority = "Standard"

    # --- Reason (must cite description words) ---
    reason = _build_reason(description, category, urgency_matches, cat_keywords)

    # --- Flag ---
    flag = "NEEDS_REVIEW" if needs_review else ""

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ---------------------------------------------------------------------------
# Batch skill: batch_classify  (skills.md → batch_classify)
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.

    - Appends category, priority, reason, flag columns to every row.
    - Skips and logs rows that cause errors (does not crash).
    - Flags null / malformed rows.
    - Always produces an output file even if some rows fail.
    """
    results: list[dict] = []

    try:
        with open(input_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for line_no, row in enumerate(reader, start=2):  # 1-indexed; row 1 = header
                try:
                    classification = classify_complaint(row)
                    merged = {**row, **classification}
                    results.append(merged)
                except Exception as exc:
                    logging.warning("Row %d skipped due to error: %s", line_no, exc)
                    # Emit a flagged row so nothing is silently lost
                    merged = {
                        **row,
                        "complaint_id": row.get("complaint_id", ""),
                        "category":     "Other",
                        "priority":     "Low",
                        "reason":       f"Row processing error: {exc}",
                        "flag":         "NEEDS_REVIEW",
                    }
                    results.append(merged)
    except FileNotFoundError:
        logging.error("Input file not found: %s", input_path)
        raise

    # Determine fieldnames: original columns + classification columns
    if results:
        # Preserve original column order, then append new ones at the end
        base_fields = list(results[0].keys())
        extra = [c for c in ["category", "priority", "reason", "flag"]
                 if c not in base_fields]
        fieldnames = base_fields + extra
    else:
        fieldnames = OUTPUT_COLUMNS

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Municipal Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input CSV (test_[city].csv)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
