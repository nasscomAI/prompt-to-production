"""
UC-0A — Complaint Classifier  |  app.py
========================================
Implements the two skills defined in skills.md and all enforcement rules
from agents.md, driven by the schema in README.md.

Run:
    python app.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Schema constants — agents.md enforcement rules 1, 2, 5, 6
# ─────────────────────────────────────────────────────────────────────────────

# enforcement rule 1 & 6: exact strings only — no variations or hallucinated values
ALLOWED_CATEGORIES: frozenset[str] = frozenset({
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
})

ALLOWED_PRIORITIES: frozenset[str] = frozenset({"Urgent", "Standard", "Low"})

# enforcement rule 2: any of these keywords → priority must be Urgent
URGENT_KEYWORDS: tuple[str, ...] = (
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
)

# enforcement rule 5: category detection — keywords map to exact taxonomy strings
# Order matters: more specific patterns are listed first
CATEGORY_SIGNALS: list[tuple[str, tuple[str, ...]]] = [
    ("Heritage Damage",  ("heritage", "monument", "historical", "ancient", "heritage site")),
    ("Heat Hazard",      ("heat hazard", "heat wave", "scorching heat", "thermal risk")),
    ("Drain Blockage",   ("drain block", "blocked drain", "drainage block", "clogged drain",
                          "sewer block", "manhole overflow", "drain overflow")),
    ("Road Damage",      ("road damage", "broken road", "cracked road", "damaged road",
                          "road crack", "road broken", "uneven road", "road collapsed")),
    ("Streetlight",      ("streetlight", "street light", "lamp post", "light post",
                          "light pole", "no light", "dark street", "lights not working")),
    ("Flooding",         ("flood", "flooded", "waterlogged", "submerged", "inundated",
                          "water logging", "water stagnation")),
    ("Pothole",          ("pothole", "pot hole", "pot-hole", "crater on road",
                          "road pit", "hole in road")),
    ("Waste",            ("garbage", "waste", "trash", "litter", "dumping",
                          "rubbish", "overflowing bin", "waste bin", "garbage bin")),
    ("Noise",            ("noise", "loud", "honking", "blaring music", "sound disturbance",
                          "noise pollution", "loud noise")),
    ("Heat Hazard",      ("heat", "hot temperature", "extreme heat")),  # broader fallback
    ("Drain Blockage",   ("drain", "sewer", "manhole")),               # broader fallback
]

# Secondary signals for Standard vs Low when no urgent keyword fires
STANDARD_SIGNALS: tuple[str, ...] = (
    "broken", "damaged", "blocked", "not working", "overflowing",
    "danger", "unsafe", "leaking", "collapsed", "cracked",
)


# ─────────────────────────────────────────────────────────────────────────────
# Skill 1 — classify_complaint  (skills.md)
# ─────────────────────────────────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single citizen complaint row.

    Input:  dict containing at least 'description' (raw complaint text).
    Output: dict with keys — complaint_id, category, priority, reason, flag.

    Enforcement (agents.md):
      1. category ∈ ALLOWED_CATEGORIES only
      2. priority = Urgent if any URGENT_KEYWORDS in description
      3. reason cites specific words from description
      4. flag = NEEDS_REVIEW when ambiguous
      5. no taxonomy drift — exact strings only
      6. no hallucinated subcategories
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description  = str(row.get("description", "")).strip()

    # skills.md error_handling: empty / unparseable description
    if not description:
        return _safe_default(complaint_id, "Description missing or unreadable.")

    desc_lower = description.lower()

    # ── enforcement rule 2: urgent keyword check (highest priority) ──────────
    urgent_hit: Optional[str] = _first_urgent_keyword(desc_lower)
    priority = "Urgent" if urgent_hit else _standard_or_low(desc_lower)

    # ── enforcement rules 1, 4, 5, 6: category detection ────────────────────
    category, matched_signal, is_ambiguous = _detect_category(desc_lower)

    # ── enforcement rule 3: reason must cite description words ───────────────
    reason = _build_reason(category, matched_signal, urgent_hit, is_ambiguous)

    # ── enforcement rule 4: flag on ambiguity ────────────────────────────────
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Skill 2 — batch_classify  (skills.md)
# ─────────────────────────────────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, apply classify_complaint to every row, write results CSV.

    Input:  Path to test_[city].csv — 15 rows, category + priority_flag stripped.
    Output: results_[city].csv — all original columns + category, priority, reason, flag.

    Error handling (skills.md):
      - Bad row → safe defaults + NEEDS_REVIEW, log to stderr, continue.
      - File not found → exit with non-zero status, no partial output.
    """
    results: list[dict] = []
    error_count = 0

    # skills.md error_handling: file not found → non-zero exit, no partial output
    try:
        with open(input_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for idx, row in enumerate(reader, start=1):
                try:
                    classification = classify_complaint(row)
                    results.append({**row, **classification})
                except Exception as exc:
                    error_count += 1
                    print(
                        f"[WARN] Row {idx} — classification error: {exc}. "
                        f"Writing NEEDS_REVIEW default.",
                        file=sys.stderr,
                    )
                    results.append({
                        **row,
                        **_safe_default(
                            str(row.get("complaint_id", f"row_{idx}")),
                            "Row processing error — could not classify.",
                        ),
                    })
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print("[WARN] No rows were processed — output file will be empty.", file=sys.stderr)

    # Preserve all input columns; append classification cols without duplication
    ordered_fields = list(dict.fromkeys(
        list(results[0].keys()) if results else
        ["complaint_id", "description", "category", "priority", "reason", "flag"]
    ))

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=ordered_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"[INFO] {len(results)} row(s) written to {output_path}")
    if error_count:
        print(
            f"[INFO] {error_count} row(s) failed classification and were written "
            f"with NEEDS_REVIEW defaults.",
            file=sys.stderr,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _first_urgent_keyword(desc_lower: str) -> Optional[str]:
    """Return the first URGENT_KEYWORDS match, or None."""
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            return kw
    return None


def _detect_category(desc_lower: str) -> tuple[str, str, bool]:
    """
    Return (category, matched_signal, is_ambiguous).

    Scans CATEGORY_SIGNALS in specificity order.
    - 1 match  → confident, is_ambiguous = False
    - >1 match → pick first, is_ambiguous = True  (enforcement rule 4)
    - 0 matches → Other + NEEDS_REVIEW             (enforcement rules 1, 4)

    enforcement rules 5 & 6: only ALLOWED_CATEGORIES strings are ever returned.
    """
    seen_categories: list[str] = []
    first_signal: str = ""

    for category, signals in CATEGORY_SIGNALS:
        if category in seen_categories:
            continue                              # already matched this category
        for sig in signals:
            if sig in desc_lower:
                if not seen_categories:
                    first_signal = sig            # record first matched keyword
                if category not in seen_categories:
                    seen_categories.append(category)
                break

    if len(seen_categories) == 1:
        return seen_categories[0], first_signal, False
    elif len(seen_categories) > 1:
        return seen_categories[0], first_signal, True     # ambiguous
    else:
        return "Other", "", True                          # no match → NEEDS_REVIEW


def _standard_or_low(desc_lower: str) -> str:
    """Assign Standard or Low when no urgent keyword fires."""
    for sig in STANDARD_SIGNALS:
        if sig in desc_lower:
            return "Standard"
    return "Low"


def _build_reason(
    category: str,
    matched_signal: str,
    urgent_hit: Optional[str],
    is_ambiguous: bool,
) -> str:
    """
    Compose a one-sentence reason that cites description words.
    enforcement rule 3: reason must reference specific words from the description.
    """
    if is_ambiguous and not matched_signal:
        return (
            "Category could not be determined from the description text alone; "
            "no matching signal found."
        )
    if is_ambiguous:
        base = (
            f"Description matches multiple categories; classified as {category} "
            f"based on '{matched_signal}' but marked for review due to ambiguity."
        )
    else:
        base = f"Classified as {category} because description contains '{matched_signal}'."

    if urgent_hit:
        base = base.rstrip(".") + (
            f"; priority set to Urgent because description contains '{urgent_hit}'."
        )

    return base


def _safe_default(complaint_id: str, reason: str) -> dict:
    """Return a safe NEEDS_REVIEW default — used by both error-handling paths."""
    return {
        "complaint_id": complaint_id,
        "category":     "Other",
        "priority":     "Low",
        "reason":       reason,
        "flag":         "NEEDS_REVIEW",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Entry point  —  README run command:
#   python app.py --input ../data/city-test-files/test_pune.csv
#                 --output results_pune.csv
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier — classifies city complaint CSVs.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV, e.g. ../data/city-test-files/test_pune.csv",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV, e.g. results_pune.csv",
    )
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
