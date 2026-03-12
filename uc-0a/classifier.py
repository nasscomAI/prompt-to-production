"""
UC-0A — Complaint Classifier
Deterministic keyword-based classifier following RICE enforcement rules.
Addresses: taxonomy drift, severity blindness, missing justification,
hallucinated sub-categories, false confidence on ambiguity.
"""
import argparse
import csv
import re
import sys

# ── Allowed values (exact strings, no variations) ──────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# ── Severity keywords → Urgent priority ────────────────────────────────────
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

# ── Category keyword patterns (order matters for ambiguity detection) ──────
# Each tuple: (category_name, compiled_regex, human-readable keyword list)
CATEGORY_PATTERNS = [
    ("Pothole",        re.compile(r"pothole|pot\s*hole", re.IGNORECASE),
     ["pothole"]),
    ("Flooding",       re.compile(r"flood|waterlog|submerge|knee[- ]?deep|water\s*level|inundat", re.IGNORECASE),
     ["flood", "waterlog", "knee-deep"]),
    ("Streetlight",    re.compile(r"streetlight|street\s*light|lamp\s*post|lights?\s+out|light\s+out|flickering|sparking", re.IGNORECASE),
     ["streetlight", "lights out", "flickering"]),
    ("Waste",          re.compile(r"garbage|waste|rubbish|trash|dumped|overflowing|dead\s*animal|litter|refuse|sewage|bins", re.IGNORECASE),
     ["garbage", "waste", "dumped", "overflowing"]),
    ("Noise",          re.compile(r"noise|loud|music|honking|midnight|decibel|blaring", re.IGNORECASE),
     ["noise", "music", "midnight"]),
    ("Road Damage",    re.compile(r"crack|sinking|broken.*(?:road|footpath|pavement|tile)|(?:road|footpath|pavement).*broken|manhole|cave[- ]?in|upturned", re.IGNORECASE),
     ["crack", "sinking", "broken", "manhole", "footpath"]),
    ("Heritage Damage", re.compile(r"heritage|historic|monument|old\s*city|ancient", re.IGNORECASE),
     ["heritage", "historic", "old city"]),
    ("Heat Hazard",    re.compile(r"heat|heatwave|sun\s*stroke|hot\s*surface|thermal", re.IGNORECASE),
     ["heat", "heatwave", "sunstroke"]),
    ("Drain Blockage", re.compile(r"drain|blocked\s*drain|drain\s*block|clogged|storm\s*water|nala|gutter", re.IGNORECASE),
     ["drain", "blocked", "clogged"]),
]


def _find_severity_matches(description: str) -> list[str]:
    """Return list of severity keywords found in description."""
    desc_lower = description.lower()
    found = []
    for kw in SEVERITY_KEYWORDS:
        # Use word boundary matching to avoid partial matches
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            found.append(kw)
    return found


def _find_category_matches(description: str) -> list[tuple[str, list[str]]]:
    """Return list of (category, matched_terms) for all matching categories."""
    matches = []
    for cat_name, pattern, keywords in CATEGORY_PATTERNS:
        found_terms = pattern.findall(description)
        if found_terms:
            matches.append((cat_name, [t.strip() for t in found_terms]))
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules:
    1. Category must be exactly one of the 10 allowed values
    2. Priority is Urgent if severity keywords present
    3. Reason cites specific words from description
    4. Flag is NEEDS_REVIEW when category is genuinely ambiguous
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Handle missing description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }

    # ── Step 1: Find all matching categories ──
    category_matches = _find_category_matches(description)

    if len(category_matches) == 0:
        category = "Other"
        flag = ""
        cat_evidence = "no recognized category keywords"
    elif len(category_matches) == 1:
        category = category_matches[0][0]
        flag = ""
        cat_evidence = ", ".join(category_matches[0][1])
    else:
        # Multiple categories match → pick first but flag as ambiguous
        category = category_matches[0][0]
        flag = "NEEDS_REVIEW"
        all_cats = [m[0] for m in category_matches]
        cat_evidence = ", ".join(category_matches[0][1]) + \
            f" (also matches: {', '.join(all_cats[1:])})"

    # ── Step 2: Determine priority via severity keywords ──
    severity_matches = _find_severity_matches(description)

    if severity_matches:
        priority = "Urgent"
    elif category == "Noise":
        # Noise complaints without severity keywords default to Low
        priority = "Low"
    else:
        priority = "Standard"

    # ── Step 3: Build reason citing specific description words ──
    if severity_matches:
        reason = (
            f"Classified as {category} based on '{cat_evidence}'; "
            f"Urgent due to severity keyword(s): {', '.join(severity_matches)}."
        )
    else:
        reason = (
            f"Classified as {category} based on '{cat_evidence}' found in description."
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Resilient: does not crash on bad rows; logs errors to stderr.
    """
    results = []
    errors = 0

    with open(input_path, "r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                errors += 1
                print(f"[ERROR] Row {i}: {e}", file=sys.stderr)

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints ({errors} errors). "
          f"Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
