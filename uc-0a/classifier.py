"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.

Enforcement rules (agents.md):
  - category must be exactly one of the 10 allowed values; never invented labels
  - priority is Urgent iff a severity keyword is present; otherwise Standard/Low
  - every output row includes a reason sentence citing words from the description
  - flag is NEEDS_REVIEW when the category is genuinely ambiguous
  - every input row produces exactly one output row; no rows skipped or merged
  - reason must reference words actually present in the source description
"""

import argparse
import csv
import sys
import warnings
from typing import Optional

# ---------------------------------------------------------------------------
# Closed taxonomy — agents.md: no values outside this list are ever permitted
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

# ---------------------------------------------------------------------------
# Severity keywords — agents.md: any match forces priority = Urgent
# ---------------------------------------------------------------------------
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ---------------------------------------------------------------------------
# Category keyword map — ordered from most-specific to least-specific.
# Each entry: (category_label, [keywords_that_signal_this_category])
# Words are matched case-insensitively against the full description.
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Heritage Damage",  ["heritage", "monument", "historical", "historic",
                          "ancient", "cultural site", "fort", "temple damage",
                          "archaeological"]),
    ("Heat Hazard",      ["heat hazard", "heat wave", "heatwave", "scorching",
                          "heat stroke", "overheating", "sun stroke"]),
    ("Drain Blockage",   ["drain blockage", "blocked drain", "drain block",
                          "drain", "drainage", "sewer", "manhole", "gutter",
                          "clogged", "choked pipe"]),
    ("Flooding",         ["flood", "waterlog", "water log", "inundat",
                          "submerged", "standing water", "overflow", "water stagnation"]),
    ("Streetlight",      ["streetlight", "street light", "lamp post", "lamppost",
                          "light out", "no light", "dark street", "street lamp",
                          "light broken", "light not working"]),
    ("Pothole",          ["pothole", "pot hole", "pit on road", "crater",
                          "hole in road", "sunken road", "road pit"]),
    ("Road Damage",      ["road damage", "road crack", "road broken",
                          "broken road", "damaged road", "road surface",
                          "tarmac", "asphalt crack", "road condition",
                          "road deteriorat"]),
    ("Noise",            ["noise", "loud", "blaring", "honking",
                          "noise pollution", "sound disturbance", "nuisance sound",
                          "disturbance"]),
    ("Waste",            ["garbage", "waste", "trash", "litter", "dump",
                          "rubbish", "refuse", "filth", "garbage dump",
                          "solid waste", "open dump"]),
]


def _find_matching_keywords(text: str, keywords: list[str]) -> list[str]:
    """Return every keyword from `keywords` that appears in `text` (case-insensitive)."""
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def _determine_category(description: str) -> tuple[str, list[str], bool]:
    """
    Return (category, matched_keywords, is_ambiguous).

    Iterates CATEGORY_KEYWORDS in priority order. Collects all categories that
    match at least one keyword. If exactly one matches → clear classification.
    If more than one matches → pick the first (highest-priority) and set
    is_ambiguous = True so the caller can raise NEEDS_REVIEW.
    If none match → Other.
    """
    matches: list[tuple[str, list[str]]] = []
    for category, keywords in CATEGORY_KEYWORDS:
        found = _find_matching_keywords(description, keywords)
        if found:
            matches.append((category, found))

    if not matches:
        return "Other", [], False
    if len(matches) == 1:
        cat, found_kws = matches[0]
        return cat, found_kws, False
    # Multiple categories matched — ambiguous
    best_cat, best_kws = matches[0]
    return best_cat, best_kws, True


def _determine_priority(description: str) -> tuple[str, list[str]]:
    """
    Return (priority, triggered_keywords).

    agents.md: priority = Urgent iff ANY severity keyword is present.
    Otherwise Standard. Low is reserved for rows with no description.
    """
    triggered = _find_matching_keywords(description, SEVERITY_KEYWORDS)
    if triggered:
        return "Urgent", triggered
    return "Standard", []


def _build_reason(
    description: str,
    category: str,
    category_kws: list[str],
    priority: str,
    severity_kws: list[str],
) -> str:
    """
    Build a one-sentence reason that cites actual words from the description.
    agents.md: reason must reference words present in the source — never fabricated.
    """
    cited: list[str] = []
    # Prefer the matched category keywords as primary evidence
    if category_kws:
        cited.extend(f'"{kw}"' for kw in category_kws[:2])
    # Also note severity trigger if present
    if severity_kws:
        cited.extend(f'"{kw}"' for kw in severity_kws[:2])

    if cited:
        evidence = ", ".join(cited)
        if severity_kws:
            return (
                f"Classified as {category} ({priority}) because the description "
                f"contains {evidence}."
            )
        return (
            f"Classified as {category} because the description contains {evidence}."
        )
    # Fallback — no keywords cited; category defaulted to Other
    return f"No specific category keywords found; defaulted to {category}."


# ---------------------------------------------------------------------------
# Public skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint
    Input:  a single complaint record (dict) with at minimum a 'description' field.
    Output: dict with keys complaint_id, category, priority, reason, flag.

    Enforcement rules applied:
      - category is always one of the 10 allowed values (never invented)
      - priority is Urgent iff a severity keyword appears in description
      - reason cites specific words found in description
      - flag is NEEDS_REVIEW when category is ambiguous or description is missing
      - composite / sub-category strings are never produced
    """
    complaint_id: str = row.get("complaint_id", row.get("id", ""))
    description: Optional[str] = row.get("description", None)

    # --- Error handling: missing or empty description ---
    if not description or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    description = str(description).strip()

    # --- Determine category ---
    category, category_kws, is_ambiguous = _determine_category(description)

    # --- Determine priority (severity keywords override everything) ---
    priority, severity_kws = _determine_priority(description)

    # --- Build reason (must cite source words) ---
    reason = _build_reason(description, category, category_kws, priority, severity_kws)

    # --- Set flag ---
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    # --- Validate category is in allowed list (safety guard) ---
    assert category in ALLOWED_CATEGORIES, (
        f"BUG: produced category '{category}' which is not in the allowed taxonomy."
    )
    # --- Validate priority is in allowed list ---
    assert priority in ("Urgent", "Standard", "Low"), (
        f"BUG: produced priority '{priority}' which is not in [Urgent, Standard, Low]."
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Public skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Skill: batch_classify
    Input:  file path to a CSV (test_[city].csv) with a 'description' column.
    Output: CSV written to output_path with original columns + category, priority,
            reason, flag appended — one output row per input row, same order.

    Error handling:
      - If input file cannot be opened/parsed → print error and halt (no partial output)
      - If an individual row is missing a description → apply classify_complaint
        error handling for that row and continue
      - If output is not writable → print error and halt
      - Rows where flag = NEEDS_REVIEW are logged as warnings
    """
    # --- Read all input rows first so we don't write partial output on read errors ---
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                print(f"ERROR: '{input_path}' appears to be empty or has no header row.",
                      file=sys.stderr)
                sys.exit(1)
            input_rows = list(reader)
            original_fieldnames = list(reader.fieldnames)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: '{input_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Could not parse input file '{input_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Classify every row ---
    output_rows: list[dict] = []
    for row in input_rows:
        result = classify_complaint(row)
        merged = dict(row)
        merged["category"] = result["category"]
        merged["priority"] = result["priority"]
        merged["reason"] = result["reason"]
        merged["flag"] = result["flag"]
        output_rows.append(merged)

        if result["flag"] == "NEEDS_REVIEW":
            complaint_id = result.get("complaint_id", row.get("complaint_id", "?"))
            warnings.warn(
                f"NEEDS_REVIEW — complaint_id={complaint_id}: "
                f"category '{result['category']}' is ambiguous or description missing.",
                UserWarning,
                stacklevel=2,
            )

    # --- Write output (halt cleanly if not writable) ---
    output_fieldnames = original_fieldnames.copy()
    for col in ("category", "priority", "reason", "flag"):
        if col not in output_fieldnames:
            output_fieldnames.append(col)

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(output_rows)
    except OSError as exc:
        print(f"ERROR: Cannot write to output file '{output_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    needs_review_count = sum(1 for r in output_rows if r.get("flag") == "NEEDS_REVIEW")
    print(f"Classified {len(output_rows)} complaints — "
          f"{needs_review_count} flagged NEEDS_REVIEW.")


# ---------------------------------------------------------------------------
# Entry point — matches the run command in the UC README:
#   python classifier.py --input ../data/city-test-files/test_pune.csv
#                        --output results_pune.csv
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
