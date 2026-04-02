"""
UC-0A — Complaint Classifier
Rule-based civic complaint classifier built from agents.md + skills.md specs.

Enforcement rules (from agents.md):
  - Category must be exactly one of the allowed values.
  - Priority must be 'Urgent' if severity keywords are present.
  - Every output includes a 'reason' citing specific words from the description.
  - Ambiguous complaints → category 'Other', flag 'NEEDS_REVIEW'.
"""

import argparse
import csv
import re
import sys

# ── Schema constants (from README.md) ────────────────────────────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ── Category keyword map ─────────────────────────────────────────────────────
# Each entry maps a category to a list of keywords / phrases that signal it.
# Order matters: more specific categories are checked first.

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Pothole":         ["pothole", "pot hole", "tyre damage", "tire damage"],
    "Flooding":        ["flood", "flooded", "waterlog", "water-log", "submerge",
                        "knee-deep", "inundate", "stranded"],
    "Streetlight":     ["streetlight", "street light", "lights out", "light out",
                        "dark at night", "flickering", "sparking", "lamp post"],
    "Waste":           ["garbage", "waste", "rubbish", "trash", "dumped",
                        "overflowing", "dead animal", "debris", "litter",
                        "not removed", "bulk waste"],
    "Noise":           ["noise", "loud music", "music past midnight",
                        "decibel", "honking", "loudspeaker"],
    "Road Damage":     ["road surface", "cracked", "sinking", "broken road",
                        "manhole", "footpath", "tiles broken", "upturned",
                        "road crack", "cave-in"],
    "Heritage Damage": ["heritage", "monument", "historical", "archaeological",
                        "ancient structure"],
    "Heat Hazard":     ["heat", "heatwave", "sunstroke", "heat stroke",
                        "temperature", "heat hazard"],
    "Drain Blockage":  ["drain block", "drain clog", "blocked drain",
                        "clogged drain", "drain overflow", "nullah",
                        "stormwater", "sewer block"],
}


# ── Skill 1: classify_complaint ──────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input : dict with at least 'complaint_id' and 'description' keys.
    Output: dict with keys  complaint_id, category, priority, reason, flag.

    Error handling (from skills.md):
        - Missing / empty description → category 'Other', flag 'NEEDS_REVIEW'.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description: str = str(row.get("description") or "").strip()

    # ── Guard: missing description ────────────────────────────────────────
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Determine category ────────────────────────────────────────────────
    category = None
    matched_keyword = None

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                matched_keyword = kw
                break
        if category:
            break

    # ── Handle ambiguity ──────────────────────────────────────────────────
    flag = ""
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"
        matched_keyword = None

    # ── Determine priority ────────────────────────────────────────────────
    severity_matches = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if severity_matches:
        priority = "Urgent"
    else:
        priority = "Standard"

    # ── Build reason (must cite specific words from description) ──────────
    if severity_matches and matched_keyword:
        reason = (
            f"Classified as '{category}' due to keyword '{matched_keyword}'; "
            f"marked Urgent because description contains: "
            f"{', '.join(severity_matches)}."
        )
    elif matched_keyword:
        reason = (
            f"Classified as '{category}' because description mentions "
            f"'{matched_keyword}'."
        )
    else:
        reason = (
            "Category could not be determined from the description; "
            "flagged for manual review."
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ── Skill 2: batch_classify ─────────────────────────────────────────────────

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.

    Error handling (from skills.md):
        - Flags null / empty rows without crashing.
        - Catches per-row errors so remaining rows still produce output.
        - Prints warnings to stderr for any problematic rows.
    """
    results: list[dict] = []
    errors: int = 0

    # ── Read & classify ───────────────────────────────────────────────────
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # row 1 = header
                try:
                    # Skip completely empty rows
                    if all(not v for v in row.values()):
                        print(
                            f"[WARN] Row {row_num}: empty row skipped.",
                            file=sys.stderr,
                        )
                        errors += 1
                        continue

                    result = classify_complaint(row)
                    results.append(result)
                except Exception as exc:
                    errors += 1
                    print(
                        f"[ERROR] Row {row_num}: {exc}",
                        file=sys.stderr,
                    )
                    # Still produce a row so the output count matches
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {exc}",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        print(f"[FATAL] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # ── Write results ─────────────────────────────────────────────────────
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints ({errors} warnings/errors).")


# ── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
