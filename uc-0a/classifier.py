"""
UC-0A — Complaint Classifier
Built using the RICE (agents.md) -> skills.md -> CRAFT workflow.
"""
import argparse
import csv
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]
ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Keyword hits are matched case-insensitively against the description text.
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "waterlogging", "water logging", "inundat"],
    "Streetlight": [
        "streetlight", "streetlights", "street light", "street lights",
        "lamppost", "lamp post", "light not working", "lights not working", "dark street",
    ],
    "Waste": ["garbage", "trash", "waste", "dumping", "dumped", "litter", "rubbish"],
    "Noise": ["noise", "loud music", "loudspeaker", "honking", "blaring horn", "decibel"],
    "Road Damage": [
        "road damage", "road crack", "cracked road", "broken road",
        "road caved", "road cave-in", "damaged road", "road collapsed",
    ],
    "Heritage Damage": ["heritage", "monument", "historic structure", "historic building"],
    "Heat Hazard": ["heatstroke", "sunstroke", "heat wave", "heatwave", "extreme heat", "heat hazard"],
    "Drain Blockage": [
        "drain block", "blocked drain", "drain blocked", "clogged drain",
        "sewage overflow", "drain overflow", "choked drain",
    ],
}

# Per agents.md enforcement: these must always force priority to Urgent.
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse",
]

LOW_PRIORITY_KEYWORDS = ["minor", "slight", "occasional", "small crack", "flicker"]


def _find_matches(description_lower, keyword_map):
    matches = {}
    for label, keywords in keyword_map.items():
        found = [kw for kw in keywords if kw in description_lower]
        if found:
            matches[label] = found
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description was provided, so the complaint cannot be classified with confidence.",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()

    category_matches = _find_matches(description_lower, CATEGORY_KEYWORDS)
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]

    flag = ""
    if not category_matches:
        category = "Other"
        flag = "NEEDS_REVIEW"
        category_clause = "no matching category keywords were found in the description"
    elif len(category_matches) > 1:
        # Genuinely ambiguous: more than one category has supporting evidence.
        category = max(category_matches, key=lambda c: len(category_matches[c]))
        flag = "NEEDS_REVIEW"
        evidence = "; ".join(
            f"{cat} ('{', '.join(kws)}')" for cat, kws in category_matches.items()
        )
        category_clause = f"description contains indicators for more than one category ({evidence}), so it is genuinely ambiguous"
    else:
        category = next(iter(category_matches))
        matched_keyword = category_matches[category][0]
        category_clause = f"description mentions '{matched_keyword}'"

    if severity_hits:
        priority = "Urgent"
        priority_clause = f"priority set to Urgent because the description mentions '{severity_hits[0]}'"
    elif any(kw in description_lower for kw in LOW_PRIORITY_KEYWORDS):
        priority = "Low"
        low_kw = next(kw for kw in LOW_PRIORITY_KEYWORDS if kw in description_lower)
        priority_clause = f"priority set to Low because the description mentions '{low_kw}'"
    else:
        priority = "Standard"
        priority_clause = "priority set to Standard as no severity keywords were found"

    # Defensive guard: never emit a value outside the allowed schema.
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    reason = f"Classified as {category}: {category_clause}; {priority_clause}."

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
    Guarantees: output row count always equals input row count; a malformed
    or failing row is still emitted (Other/Low/NEEDS_REVIEW) rather than dropped.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file not found: {input_path}. Expected a CSV at this path (e.g. ../data/city-test-files/test_[city].csv)."
        ) from None

    if not fieldnames:
        raise ValueError(f"Input file has no header row: {input_path}")

    output_fieldnames = list(fieldnames) + ["category", "priority", "reason", "flag"]
    output_rows = []

    for row in rows:
        try:
            classified = classify_complaint(row)
        except Exception as exc:
            classified = {
                "category": "Other",
                "priority": "Low",
                "reason": f"Row could not be classified due to a processing error ({exc}); marked for manual review.",
                "flag": "NEEDS_REVIEW",
            }

        if classified.get("category") not in ALLOWED_CATEGORIES:
            classified["category"] = "Other"
            classified["flag"] = "NEEDS_REVIEW"
        if classified.get("priority") not in ALLOWED_PRIORITIES:
            classified["priority"] = "Standard"

        merged = dict(row)
        merged["category"] = classified["category"]
        merged["priority"] = classified["priority"]
        merged["reason"] = classified.get("reason", "")
        merged["flag"] = classified.get("flag", "")
        output_rows.append(merged)

    assert len(output_rows) == len(rows), "Output row count must match input row count."

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        for r in output_rows:
            writer.writerow({k: r.get(k, "") for k in output_fieldnames})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Done. Results written to {args.output}")
