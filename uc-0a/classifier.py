"""
UC-0A — Complaint Classifier
Implements agents.md + skills.md: classify_complaint per row, batch_classify delegates to it.

If you see errors mentioning Python 3.4 or "__future__.annotations", your PYTHONHOME / PYTHONPATH
points at an old Python. In CMD run:  set PYTHONHOME=  &  set PYTHONPATH=
"""
import os
import sys

# Must run before any other imports: python312.exe + PYTHONHOME can load Python 3.4 stdlib and crash.
_ph = (os.environ.get("PYTHONHOME") or "").replace("/", "\\")
if _ph and "Python34" in _ph:
    sys.stderr.write(
        "ERROR: PYTHONHOME is set to an old Python ({0}).\n"
        "Run before classifier.py:\n"
        "  set PYTHONHOME=\n"
        "  set PYTHONPATH=\n".format(_ph)
    )
    sys.exit(1)

if sys.version_info < (3, 9):
    sys.exit("Python 3.9+ required. This process reports: " + sys.version)

import argparse
import csv
import logging
from typing import Any, Dict, List, Tuple

# --- Schema (agents.md / README) ---
ALLOWED_CATEGORIES = (
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
)
ALLOWED_PRIORITIES = ("Urgent", "Standard", "Low")

URGENCY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

# Weighted keyword groups: higher score wins; ties -> Other + NEEDS_REVIEW
CATEGORY_SIGNALS: List[Tuple[str, Tuple[str, ...]]] = [
    ("Heat Hazard", ("heat hazard", "heat stroke", "sunstroke")),
    ("Heritage Damage", ("heritage", "heritage street", "old city")),
    (
        "Flooding",
        ("flooded", "flooding", "flood", "knee-deep", "stranded", "in water"),
    ),
    ("Drain Blockage", ("drain", "manhole", "sewage", "drainage")),
    ("Pothole", ("pothole", "potholes")),
    (
        "Streetlight",
        ("streetlight", "street light", "lights out", "flickering", "sparking", "very dark"),
    ),
    (
        "Waste",
        ("garbage", "bins", "overflowing", "dead animal", "smell", "bulk waste", "dumped", "waste"),
    ),
    ("Noise", ("music", "midnight", "noise", "loud", "venue")),
    (
        "Road Damage",
        ("cracked", "sinking", "road surface", "footpath", "upturned", "tiles broken", "utility work"),
    ),
]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _description_from_row(row: Dict[str, Any]) -> str:
    """skills.md: use description; tolerate key casing."""
    if not row:
        return ""
    for key in ("description", "Description", "text", "complaint_text"):
        v = row.get(key)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


def _score_categories(lower: str) -> Dict[str, int]:
    scores: Dict[str, int] = {c: 0 for c in ALLOWED_CATEGORIES if c != "Other"}
    for cat, phrases in CATEGORY_SIGNALS:
        for ph in phrases:
            if ph in lower:
                scores[cat] += len(ph)
    return scores


def _best_category(lower: str, scores: Dict[str, int]) -> Tuple[str, bool]:
    """
    Returns (category, ambiguous_tie).
    If no signal, Other + NEEDS_REVIEW.
    If tie on max score, break ties when Flooding vs Drain is common; else Other + NEEDS_REVIEW.
    """
    if not scores:
        return "Other", True
    best = max(scores.values())
    if best <= 0:
        return "Other", True
    leaders = [c for c, s in scores.items() if s == best]
    if len(leaders) > 1:
        flood_markers = ("flooded", "flooding", "flood", "knee-deep", "stranded")
        if "Flooding" in leaders and any(m in lower for m in flood_markers):
            return "Flooding", False
        if set(leaders) == {"Drain Blockage", "Flooding"}:
            return ("Flooding", False) if any(m in lower for m in flood_markers) else ("Drain Blockage", False)
        return "Other", True
    cat = leaders[0]
    # Flooding vs Drain when drain wins score but inundation language is present
    if cat == "Drain Blockage" and any(w in lower for w in ("flooded", "flooding", "flood", "knee-deep")):
        if scores.get("Flooding", 0) >= best - 1:
            return "Flooding", False
    return cat, False


def _has_urgency(lower: str) -> bool:
    return any(k in lower for k in URGENCY_KEYWORDS)


def _priority(lower: str) -> str:
    return "Urgent" if _has_urgency(lower) else "Standard"


def _reason_sentence(description: str, category: str) -> str:
    """One sentence citing specific words from the description (agents.md)."""
    snippet = description.strip()
    if len(snippet) > 160:
        snippet = snippet[:157].rsplit(" ", 1)[0] + "…"
    return 'The complaint text cites phrases such as "{}" to justify {}.'.format(snippet, category)


def classify_complaint(row: Dict[str, Any]) -> Dict[str, str]:
    """
    skills.md: one row -> category, priority, reason, flag.
    Ignores withheld label columns if present in dev data.
    """
    # Do not use category / priority_flag as inputs (agents.md)
    safe = {k: v for k, v in row.items() if k not in ("category", "priority_flag")}
    desc = _description_from_row(safe)

    if not desc:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "No complaint description was provided in this row.",
            "flag": "NEEDS_REVIEW",
        }

    lower = desc.lower()
    scores = _score_categories(lower)
    category, ambiguous = _best_category(lower, scores)
    priority = _priority(lower)

    if ambiguous:
        flag = "NEEDS_REVIEW"
        if category == "Other":
            reason = (
                "Description does not map clearly to one taxonomy label: {}.".format(
                    desc[:160] + ("…" if len(desc) > 160 else "")
                )
            )
        else:
            reason = _reason_sentence(desc, category)
    else:
        flag = ""
        reason = _reason_sentence(desc, category)

    # Enforce allowed strings
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    skills.md: read CSV, classify each row via classify_complaint, write results.
    Preserves row order and original columns; appends category, priority, reason, flag.
    """
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                logger.error("Input CSV has no header row: %s", input_path)
                sys.exit(1)
            fieldnames = list(reader.fieldnames)
            rows = list(reader)
    except OSError as e:
        logger.error("Cannot read input: %s", e)
        sys.exit(1)

    out_fields = fieldnames + [
        c
        for c in ("category", "priority", "reason", "flag")
        if c not in fieldnames
    ]

    out_rows: List[Dict[str, Any]] = []
    for idx, row in enumerate(rows):
        try:
            pred = classify_complaint(row)
        except Exception as e:  # noqa: BLE001 — skills.md fallback row
            logger.exception("Row %s failed: %s", idx, e)
            pred = {
                "category": "Other",
                "priority": "Standard",
                "reason": "Processing failed for this row; see logs.",
                "flag": "NEEDS_REVIEW",
            }
        merged = dict(row)
        merged.update(pred)
        out_rows.append(merged)

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(out_rows)
    except OSError as e:
        logger.error("Cannot write output: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to {}".format(args.output))
