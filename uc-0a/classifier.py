"""
UC-0A — Complaint Classifier

Classifies citizen complaints into predefined categories and priority levels.

Agent boundary (from agents.md):
  - 10 allowed categories, 3 priority levels, no invented values.
  - Uses only the complaint description text — no external knowledge.
  - Severity keywords always map to Urgent priority.
  - Ambiguous complaints → category: Other, flag: NEEDS_REVIEW.

Skills implemented (from skills.md):
  - classify_complaint: single row → category + priority + reason + flag
  - batch_classify: input CSV → classify per row → output CSV
"""

import argparse
import csv
import re
import sys

# ---------------------------------------------------------------------------
# Classification Schema (from README / agents.md enforcement rules)
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

# Severity keywords — presence of ANY of these forces priority = Urgent
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

# ---------------------------------------------------------------------------
# Keyword mappings: category detection rules
# Each entry is (category, list-of-keyword-phrases).
# Order matters — first match wins for primary category assignment.
# ---------------------------------------------------------------------------

CATEGORY_RULES = [
    ("Pothole", [
        "pothole", "pot hole", "pot-hole",
    ]),
    ("Flooding", [
        "flood", "flooded", "flooding", "waterlog", "water-log",
        "waterlogged", "water logged", "submerged", "inundated",
        "knee-deep", "knee deep", "waist-deep", "waist deep",
    ]),
    ("Drain Blockage", [
        "drain block", "drain clog", "blocked drain", "clogged drain",
        "drain overflow", "manhole overflow", "drain choked",
        "choked drain", "sewage overflow", "nala block", "nala overflow",
    ]),
    ("Streetlight", [
        "streetlight", "street light", "street-light",
        "lamp post", "lamppost", "lamp-post",
        "light pole", "light not working", "lights out",
        "no light", "dark street", "bulb fused", "bulb not working",
    ]),
    ("Waste", [
        "garbage", "waste", "trash", "rubbish", "litter",
        "dumping", "dump", "debris", "refuse",
        "waste pile", "garbage pile", "not collected",
        "overflowing bin", "dustbin",
    ]),
    ("Noise", [
        "noise", "loud", "loudspeaker", "loud speaker",
        "honking", "horn", "blaring", "decibel",
        "noise pollution", "sound pollution",
        "disturbance", "DJ", "music at night",
    ]),
    ("Road Damage", [
        "road damage", "road crack", "cracked road",
        "broken road", "road surface", "bitumen",
        "asphalt", "road cave", "road caved",
        "road erosion", "road eroded", "road sinking",
        "road sunk", "crater",
    ]),
    ("Heritage Damage", [
        "heritage", "monument", "historical",
        "heritage site", "heritage structure",
        "heritage building", "ancient", "archaeological",
        "protected structure", "ASI",
    ]),
    ("Heat Hazard", [
        "heat", "heatwave", "heat wave", "heat stroke",
        "sunstroke", "sun stroke", "hot surface",
        "scorching", "burning road", "metal burn",
        "thermal", "overheated",
    ]),
]


def _normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation edges."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _contains_any(text: str, keywords: list[str]) -> list[str]:
    """Return the subset of keywords found in text."""
    norm = _normalize(text)
    return [kw for kw in keywords if kw.lower() in norm]


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input : dict with at least a 'description' field.
    Output: dict with keys — category, priority, reason, flag.

    Enforcement (agents.md):
      - category must be one of ALLOWED_CATEGORIES.
      - priority must be Urgent when any severity keyword is present.
      - reason must cite specific words from the description.
      - flag = NEEDS_REVIEW when category is genuinely ambiguous.
    """
    description = (row.get("description") or "").strip()

    # --- Handle empty / unintelligible descriptions -------------------------
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty or unintelligible.",
            "flag": "NEEDS_REVIEW",
        }

    # --- Determine priority via severity keywords ---------------------------
    severity_hits = _contains_any(description, SEVERITY_KEYWORDS)
    is_urgent = len(severity_hits) > 0

    # --- Determine category via keyword matching ----------------------------
    matched_categories = []
    matched_evidence = {}

    for cat, keywords in CATEGORY_RULES:
        hits = _contains_any(description, keywords)
        if hits:
            matched_categories.append(cat)
            matched_evidence[cat] = hits

    # Resolve category
    if len(matched_categories) == 0:
        # No keyword match → genuinely ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        evidence_words = []
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        evidence_words = matched_evidence[category]
    else:
        # Multiple categories matched — pick first (rule-order priority)
        # but only if the top match is clearly dominant; otherwise flag.
        category = matched_categories[0]
        evidence_words = matched_evidence[category]
        # If more than two categories matched, mark ambiguous
        if len(matched_categories) > 2:
            flag = "NEEDS_REVIEW"
        else:
            flag = ""

    # --- Set priority -------------------------------------------------------
    if is_urgent:
        priority = "Urgent"
    elif flag == "NEEDS_REVIEW":
        priority = "Low"
    else:
        # Heuristic: if description suggests significant disruption
        priority = "Standard"

    # --- Build reason sentence ----------------------------------------------
    reason_parts = []
    if evidence_words:
        reason_parts.append(
            f"Description mentions '{', '.join(evidence_words)}' "
            f"indicating {category}"
        )
    else:
        reason_parts.append(
            "No category keywords found in description"
        )

    if severity_hits:
        reason_parts.append(
            f"severity keyword(s) '{', '.join(severity_hits)}' trigger Urgent"
        )

    reason = "; ".join(reason_parts) + "."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str) -> dict:
    """
    Read input CSV, apply classify_complaint to each row, write results CSV.

    Input : input_path (CSV with 'description' column), output_path.
    Output: CSV at output_path with original columns + category, priority,
            reason, flag appended. Returns summary dict.

    Error handling (skills.md):
      - Missing/unreadable input → clear error with file path.
      - Per-row failure → log row number, flag NEEDS_REVIEW, continue.
    """
    # --- Read input ---------------------------------------------------------
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            input_fieldnames = list(reader.fieldnames or [])
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )
    except Exception as exc:
        raise RuntimeError(
            f"Unable to read input file '{input_path}': {exc}"
        )

    if not rows:
        raise ValueError(f"Input file '{input_path}' contains no data rows.")

    # --- Classify each row --------------------------------------------------
    output_fieldnames = input_fieldnames + [
        "category", "priority", "reason", "flag",
    ]
    classified_rows = []
    needs_review_count = 0
    error_rows = []

    for idx, row in enumerate(rows, start=1):
        try:
            result = classify_complaint(row)
        except Exception as exc:
            # Log the failure, mark NEEDS_REVIEW, continue
            print(
                f"WARNING: Row {idx} classification failed ({exc}). "
                f"Flagging NEEDS_REVIEW.",
                file=sys.stderr,
            )
            result = {
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error on row {idx}: {exc}",
                "flag": "NEEDS_REVIEW",
            }
            error_rows.append(idx)

        # Merge original row + classification result
        out_row = dict(row)
        out_row.update(result)
        classified_rows.append(out_row)

        if result.get("flag") == "NEEDS_REVIEW":
            needs_review_count += 1

    # --- Write output -------------------------------------------------------
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(classified_rows)

    summary = {
        "rows_processed": len(classified_rows),
        "needs_review": needs_review_count,
        "error_rows": error_rows,
    }

    print(
        f"Classified {summary['rows_processed']} rows. "
        f"NEEDS_REVIEW: {summary['needs_review']}. "
        f"Errors: {len(summary['error_rows'])}."
    )

    return summary


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
