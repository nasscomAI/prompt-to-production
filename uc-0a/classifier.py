"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify as defined in skills.md.
Enforcement rules are sourced from agents.md and README.md.

Run:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""

import argparse
import csv
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Classification Schema — must match README.md exactly
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = {
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
}

PRIORITY_LEVELS = {"Urgent", "Standard", "Low"}

# Keywords that must trigger Urgent priority (agents.md enforcement rule 2)
URGENT_KEYWORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
}

# Keyword → category mapping for classify_complaint heuristic
CATEGORY_KEYWORDS: list[tuple[str, set[str]]] = [
    ("Pothole",         {"pothole", "pot hole", "crater", "pit", "road hole"}),
    ("Flooding",        {"flood", "flooded", "flooding", "waterlogged", "submerged", "inundated"}),
    ("Streetlight",     {"streetlight", "street light", "lamp", "light post", "light pole", "dark street", "no light"}),
    ("Waste",           {"garbage", "waste", "trash", "litter", "dumping", "rubbish", "overflowing bin", "bin"}),
    ("Noise",           {"noise", "loud", "honking", "music", "sound", "disturbance", "blaring"}),
    ("Road Damage",     {"road damage", "broken road", "cracked road", "damaged road", "road crack", "uneven road"}),
    ("Heritage Damage", {"heritage", "monument", "historical", "ancient", "heritage site", "old building"}),
    ("Heat Hazard",     {"heat", "hot", "temperature", "scorching", "summer heat", "heat wave", "thermal"}),
    ("Drain Blockage",  {"drain", "blocked drain", "drainage", "sewer", "clogged", "overflow drain", "manhole"}),
]


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single citizen complaint row.

    Input:  dict with at least a 'description' key (raw complaint text).
    Output: dict with keys — complaint_id, category, priority, reason, flag.

    Enforcement (agents.md):
      - Category must be one of ALLOWED_CATEGORIES only.
      - Priority is Urgent if any URGENT_KEYWORDS appear in description.
      - Reason must cite specific words from the description.
      - Flag set to NEEDS_REVIEW when category is ambiguous.
    """
    complaint_id  = row.get("complaint_id", "").strip()
    description   = row.get("description", "").strip()

    # --- Guard: empty / unparseable description (skills.md error_handling) ---
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description missing or unreadable.",
            "flag":         "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Determine priority (enforcement rule 2) ---
    triggered_keyword = _find_urgent_keyword(desc_lower)
    priority = "Urgent" if triggered_keyword else _default_priority(desc_lower)

    # --- Determine category (enforcement rule 1) ---
    category, matched_word, is_ambiguous = _infer_category(desc_lower)

    # --- Build reason (enforcement rule 3) ---
    if triggered_keyword and is_ambiguous:
        reason = (
            f"Classified as {category} based on keyword '{matched_word}'; "
            f"marked Urgent because description contains '{triggered_keyword}'."
        )
    elif triggered_keyword:
        reason = (
            f"Classified as {category} based on '{matched_word}' in description; "
            f"priority set to Urgent because description contains '{triggered_keyword}'."
        )
    elif matched_word:
        reason = f"Classified as {category} because description contains '{matched_word}'."
    else:
        reason = "Category could not be determined from description text alone."

    # --- Set NEEDS_REVIEW flag (enforcement rule 4) ---
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, apply classify_complaint to every row, write results CSV.

    Input:  Path to test_[city].csv (15 rows, category + priority_flag stripped).
    Output: results_[city].csv with category, priority, reason, flag appended.

    Error handling (skills.md): logs bad rows and continues — never halts the batch.
    """
    output_fields = ["complaint_id", "description", "category", "priority", "reason", "flag"]
    results       = []
    errors        = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    # Preserve any extra columns from input
                    merged = {**row, **result}
                    results.append(merged)
                except Exception as e:
                    errors.append((idx, str(e)))
                    print(f"[WARN] Row {idx} failed: {e} — writing NEEDS_REVIEW default.", file=sys.stderr)
                    results.append({
                        "complaint_id": row.get("complaint_id", f"row_{idx}"),
                        "description":  row.get("description", ""),
                        "category":     "Other",
                        "priority":     "Low",
                        "reason":       "Row processing error — could not classify.",
                        "flag":         "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print("[WARN] No rows were processed. Output file will be empty.", file=sys.stderr)

    # Determine full field list (input columns + output columns, no duplicates)
    all_fields = list(dict.fromkeys(
        list(results[0].keys()) if results else output_fields
    ))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"[INFO] {len(results)} rows written to {output_path}")
    if errors:
        print(f"[INFO] {len(errors)} row(s) had errors and were written with NEEDS_REVIEW defaults.")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _find_urgent_keyword(desc_lower: str) -> Optional[str]:
    """Return the first URGENT_KEYWORDS match found, or None."""
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            return kw
    return None


def _infer_category(desc_lower: str) -> tuple[str, str, bool]:
    """
    Return (category, matched_word, is_ambiguous).

    Scans CATEGORY_KEYWORDS in order. If exactly one category matches → confident.
    If multiple categories match → pick first but mark ambiguous.
    If none match → Other + NEEDS_REVIEW.
    """
    matches: list[tuple[str, str]] = []  # (category, matched_word)

    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in desc_lower:
                matches.append((category, kw))
                break  # one match per category is enough

    if len(matches) == 1:
        return matches[0][0], matches[0][1], False   # confident
    elif len(matches) > 1:
        return matches[0][0], matches[0][1], True    # ambiguous — first wins, flag set
    else:
        return "Other", "", True                     # no match → NEEDS_REVIEW


def _default_priority(desc_lower: str) -> str:
    """Assign Standard or Low based on description tone when no urgent keyword fires."""
    standard_signals = {"broken", "damaged", "blocked", "overflowing", "not working", "danger"}
    for signal in standard_signals:
        if signal in desc_lower:
            return "Standard"
    return "Low"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier — classifies city complaint CSVs."
    )
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results_[city].csv")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
