"""
UC-0A — Complaint Classifier
Rule-based classifier implementing the RICE enforcement rules from agents.md
and the skill contracts from skills.md.
"""
import argparse
import csv
import re
import sys


# ---------------------------------------------------------------------------
# Classification schema (from agents.md enforcement rules)
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity keywords — any match → priority = Urgent (case-insensitive)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword patterns: list of (category, keywords) ordered by
# specificity so more specific categories are checked first.
# Each keyword list is matched against the lowercased description.
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Pothole",         ["pothole", "pot hole", "pot-hole"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient",
                         "archaeological"]),
    ("Heat Hazard",     ["heat hazard", "heatwave", "heat wave", "sunstroke",
                         "heat stroke", "dehydration"]),
    ("Drain Blockage",  ["drain block", "drain clog", "blocked drain",
                         "clogged drain", "choked drain", "nala block",
                         "gutter block", "sewer block", "drain overflow"]),
    ("Flooding",        ["flood", "waterlog", "water-log", "submerged",
                         "inundat", "knee-deep", "knee deep", "water level"]),
    ("Streetlight",     ["streetlight", "street light", "street-light",
                         "lights out", "lamp post", "lamp-post",
                         "bulb", "dark at night", "dark street",
                         "flickering", "sparking"]),
    ("Noise",           ["noise", "loud music", "honking", "blaring",
                         "decibel", "music past midnight", "sound pollution",
                         "noise pollution"]),
    ("Waste",           ["garbage", "waste", "trash", "rubbish", "dump",
                         "litter", "debris", "refuse", "overflowing bin",
                         "dead animal", "not removed"]),
    ("Road Damage",     ["road surface", "road crack", "road damage",
                         "cracked road", "sinking road", "broken road",
                         "uneven road", "asphalt", "tar road",
                         "footpath", "manhole", "pothole"]),
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


# ---------------------------------------------------------------------------
# Skill 1: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Implements the classify_complaint skill from skills.md:
      Input:  dict with at minimum complaint_id and description.
      Output: dict with keys: complaint_id, category, priority, reason, flag.

    Enforcement rules (agents.md):
      - Category must be exactly one of the 10 allowed values.
      - Priority is Urgent if any severity keyword is present.
      - Reason must cite specific words from the description.
      - Flag is NEEDS_REVIEW when ambiguous or description is missing.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    # --- Handle missing / empty description ---
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Determine priority via severity keywords ---
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if matched_severity:
        priority = "Urgent"
    else:
        priority = "Standard"  # default for clear civic issues

    # --- Determine category via keyword matching ---
    category_hits: list[tuple[str, list[str]]] = []
    for cat, keywords in CATEGORY_RULES:
        hits = [kw for kw in keywords if kw in desc_lower]
        if hits:
            category_hits.append((cat, hits))

    if len(category_hits) == 0:
        # No category matched — fallback to Other
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_parts = _cite_words(description)
        reason = (
            f"Description mentions '{reason_parts}' which does not clearly "
            f"match any standard category."
        )
    elif len(category_hits) == 1:
        category = category_hits[0][0]
        matched_kws = category_hits[0][1]
        flag = ""
        reason = _build_reason(description, category, priority,
                               matched_kws, matched_severity)
    else:
        # Multiple categories matched — pick the first (most specific) but
        # flag for review if the top two are from genuinely different groups.
        category = category_hits[0][0]
        matched_kws = category_hits[0][1]
        other_cats = [c for c, _ in category_hits[1:] if c != category]
        if other_cats:
            flag = "NEEDS_REVIEW"
            reason = (
                f"Description mentions '{', '.join(matched_kws)}' suggesting "
                f"{category}, but also matches {', '.join(other_cats)}; "
                f"classified as {category} with review flag."
            )
        else:
            flag = ""
            reason = _build_reason(description, category, priority,
                                   matched_kws, matched_severity)

    # If severity keywords present but category unclear, ensure Urgent + flag
    if matched_severity and flag == "NEEDS_REVIEW":
        priority = "Urgent"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Skill 2: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Implements the batch_classify skill from skills.md:
      - One output row per input row; never skip a row.
      - Malformed rows → category Other, priority Low, flag NEEDS_REVIEW.
      - Empty input (header only) → output with header only.
      - Missing input file → FileNotFoundError.
      - Warnings logged to stderr for every error-handled row.
    """
    import os
    if not os.path.isfile(input_path):
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    results: list[dict] = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # row 1 is header
            try:
                result = classify_complaint(row)
            except Exception as exc:
                cid = row.get("complaint_id", "UNKNOWN")
                print(
                    f"WARNING: Row {row_num} (complaint_id={cid}) — "
                    f"classification failed: {exc}",
                    file=sys.stderr,
                )
                result = {
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Classification failed — malformed input row",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _cite_words(description: str, max_words: int = 6) -> str:
    """Return the first few significant words from the description for citing."""
    words = description.split()
    return " ".join(words[:max_words])


def _build_reason(description: str, category: str, priority: str,
                  matched_kws: list[str], matched_severity: list[str]) -> str:
    """
    Build a one-sentence reason citing specific words from the description.
    """
    kw_cite = ", ".join(f"'{kw}'" for kw in matched_kws)

    if matched_severity:
        sev_cite = ", ".join(f"'{kw}'" for kw in matched_severity)
        return (
            f"Description contains {kw_cite} indicating {category}, "
            f"and severity keyword(s) {sev_cite} trigger {priority} priority."
        )
    else:
        return (
            f"Description contains {kw_cite} indicating {category}, "
            f"assigned {priority} priority as no severity keywords detected."
        )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
