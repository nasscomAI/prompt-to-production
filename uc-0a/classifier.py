"""
UC-0A — Complaint Classifier
Rule-based implementation derived from agents.md enforcement rules and skills.md contracts.
"""
import argparse
import csv
import sys

# agents.md › output_schema › category › allowed
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# agents.md › severity_keywords — any match forces priority: Urgent
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Ordered most-specific first so earlier patterns win on ambiguous descriptions.
# Each tuple: (category, [trigger substrings matched case-insensitively])
CATEGORY_PATTERNS = [
    ("Pothole",         ["pothole", "pot hole", "crater", "pit in road", "road pit"]),
    ("Flooding",        ["flood", "waterlog", "water log", "inundat", "submerged", "overflow"]),
    ("Streetlight",     ["streetlight", "street light", "street lamp", "lamp post",
                         "light not working", "light out", "no light", "dark road"]),
    ("Waste",           ["garbage", "waste", "trash", "rubbish", "litter", "dumping", "refuse"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient structure",
                         "temple damage", "fort damage"]),
    ("Heat Hazard",     ["heat hazard", "heatwave", "heat stroke", "extreme heat", "scorching"]),
    ("Drain Blockage",  ["drain block", "blocked drain", "drainage block", "sewer block",
                         "gutter block", "manhole block"]),
    ("Road Damage",     ["road damage", "road crack", "pavement crack", "broken road", "tar road"]),
    # Broader single-word fallbacks tried only after specific phrases above
    ("Noise",           ["noise", "loud", "blaring", "sound", "disturbance"]),
    ("Heat Hazard",     ["heat", "hot", "temperature"]),
    ("Drain Blockage",  ["drain", "sewer", "gutter", "manhole"]),
    ("Road Damage",     ["road", "pavement"]),
]


def _find_severity_hits(desc_lower: str) -> list[str]:
    return [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]


def _find_category(desc_lower: str) -> tuple[str, list[str]]:
    """Return (category, matched_keywords). Falls back to ('Other', [])."""
    for category, keywords in CATEGORY_PATTERNS:
        hits = [kw for kw in keywords if kw in desc_lower]
        if hits:
            return category, hits
    return "Other", []


def _build_reason(category: str, matched_kws: list[str], severity_hits: list[str]) -> str:
    """Construct a one-sentence reason citing specific words from the description."""
    if category == "Other":
        return "No matching category keywords found in the description; manual review required."

    cited = '", "'.join(matched_kws[:2])
    base = f'Classified as "{category}" based on "{cited}" in the description'

    if severity_hits:
        return f'{base}; priority set to Urgent due to "{severity_hits[0]}".'
    return f"{base}."


def classify_complaint(row: dict) -> dict:
    """
    skill: classify_complaint
    Input:  one CSV row dict — uses the 'description' field.
    Output: dict with keys category, priority, reason, flag.
    Error:  empty/missing description → Other / Low / NEEDS_REVIEW.
    """
    description = (
        row.get("description") or row.get("Description") or ""
    ).strip()

    complaint_id = row.get("complaint_id") or row.get("id") or ""

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description could not be interpreted.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Enforcement rule 2 — severity keywords always force Urgent
    severity_hits = _find_severity_hits(desc_lower)
    priority = "Urgent" if severity_hits else "Standard"

    # Enforcement rule 1 — category must be one of the 10 allowed values
    category, matched_kws = _find_category(desc_lower)

    # Enforcement rule 4 — ambiguous → Other + NEEDS_REVIEW
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    # Enforcement rule 3 — reason must cite specific words from the description
    reason = _build_reason(category, matched_kws, severity_hits)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    skill: batch_classify
    Input:  path to input CSV; path for output CSV.
    Output: output CSV with all original columns + category, priority, reason, flag appended.
    Error:  missing description field → classify_complaint receives ""; row still written.
            file-level errors raise with a clear message and halt.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"Input file appears empty or has no header: {input_path}")
            original_fields = list(reader.fieldnames)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except PermissionError:
        raise PermissionError(f"Cannot read input file (permission denied): {input_path}")

    new_cols = ["category", "priority", "reason", "flag"]
    output_fields = original_fields + [c for c in new_cols if c not in original_fields]

    classified_rows = []
    for row in rows:
        result = classify_complaint(row)
        out_row = dict(row)
        for col in new_cols:
            out_row[col] = result[col]
        classified_rows.append(out_row)

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(classified_rows)
    except PermissionError:
        raise PermissionError(f"Cannot write output file (permission denied): {output_path}")

    return len(classified_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    try:
        count = batch_classify(args.input, args.output)
        print(f"Done. {count} rows classified. Results written to {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
