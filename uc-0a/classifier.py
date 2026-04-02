"""
UC-0A — Complaint Classifier

Implements classify_complaint and batch_classify with full RICE enforcement:
  - Exact category names from approved list only
  - Urgent priority triggered by any severity keyword
  - Reason cites specific words from description
  - NEEDS_REVIEW flag on genuinely ambiguous classifications
"""

import argparse
import csv

# ── Allowed categories (exact strings only) ──────────────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# ── Severity keywords that must trigger Urgent ────────────────────────────────
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Extended urgency indicators derived from description patterns
EXTENDED_URGENCY_PHRASES = [
    "hospitalised", "hospitalized", "lives at risk",
    "collapsed", "ambulance diverted",
]

# ── Category keyword rules (ordered most-specific → least-specific) ───────────
# Each entry: (category_name, [keywords_to_match_in_lower_description])
CATEGORY_RULES = [
    ("Heritage Damage", ["heritage", "monument", "historical", "charminar"]),
    ("Heat Hazard",     ["heat wave", "heat hazard", "extreme heat", "heat island"]),
    ("Road Damage",     ["road collapsed", "road crack", "crater", "road damage",
                         "collapsed partially"]),
    ("Drain Blockage",  ["drain blocked", "stormwater drain", "drain completely blocked",
                         "main drain blocked", "drain blockage", "drainage blocked",
                         "sewer blocker", "sewer blocked"]),
    ("Pothole",         ["pothole", "potholes"]),
    ("Flooding",        ["flooded", "flooding", "flood", "waterlog", "floods"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "light not working",
                         "lights not", "dark road", "unlit road"]),
    ("Waste",           ["garbage overflow", "waste not cleared", "waste", "garbage",
                         "trash", "rubbish", "litter"]),
    ("Noise",           ["drilling", "idling", "engines on", "noise", "loud", "horn"]),
    # Lower-priority fallbacks
    ("Drain Blockage",  ["drain", "drainage", "mosquito breeding"]),
    ("Flooding",        ["rainwater", "floods in", "rain"]),
]


def _find_category(description: str):
    """
    Find the best category match and all matched categories.
    Returns: (primary_category, matched_keyword, all_matched_categories)
    """
    desc_lower = description.lower()
    found = []   # list of (category, matched_kw)

    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                # Add only if this category not already recorded
                if category not in [c for c, _ in found]:
                    found.append((category, kw))
                break

    if not found:
        return "Other", None, []

    all_categories = [c for c, _ in found]
    return found[0][0], found[0][1], all_categories


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement:
    - category is exactly one of the ALLOWED_CATEGORIES
    - priority is Urgent if any SEVERITY_KEYWORD found in description
    - reason cites specific words from the description
    - flag = NEEDS_REVIEW when category is genuinely ambiguous
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "UNKNOWN")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Determine category ───────────────────────────────────────────────────
    category, matched_phrase, all_categories = _find_category(description)

    # Ambiguity: 2+ distinct non-fallback categories matched
    unique_primary = list(dict.fromkeys(all_categories))  # preserve order, deduplicate
    flag = "NEEDS_REVIEW" if len(unique_primary) > 1 else ""

    # ── Determine priority ───────────────────────────────────────────────────
    triggered_kw = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            triggered_kw = kw
            break

    if triggered_kw is None:
        for phrase in EXTENDED_URGENCY_PHRASES:
            if phrase in desc_lower:
                triggered_kw = phrase
                break

    if triggered_kw:
        priority = "Urgent"
        reason = (
            f"Description contains '{triggered_kw}' — severity keyword triggers Urgent priority; "
            f"classified as {category}."
        )
    else:
        priority = "Standard"
        if matched_phrase:
            reason = (
                f"Description contains '{matched_phrase}'; classified as {category}."
            )
        else:
            reason = (
                f"No category-specific keywords matched; classified as {category} "
                f"based on context — requires manual review."
            )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    - Never crashes on bad rows; errors are recorded and execution continues
    - Outputs results even if some rows fail
    - Reports row-level errors to stdout
    """
    results = []
    errors = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):   # row 2 = first data row
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as exc:
                err_msg = f"Row {i} (id={row.get('complaint_id', '?')}): {exc}"
                errors.append(err_msg)
                results.append({
                    "complaint_id": row.get("complaint_id", f"row_{i}"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification error: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    if errors:
        print(f"WARNING: {len(errors)} row(s) had errors:")
        for e in errors:
            print(f"  {e}")

    print(f"Classified {len(results)} complaint(s). Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
