"""
UC-0A — Complaint Classifier
Built per agents.md (role/intent/context/enforcement) and skills.md
(classify_complaint, batch_classify).
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Checked in order — first match wins. Order goes most-specific to most-generic
# so a description mentioning multiple issues lands on its primary cause.
# Split into two passes around the Drain Blockage co-occurrence check (see
# classify_complaint) so "flooded ... drain blocked" still resolves to Flooding.
CATEGORY_RULES_BEFORE_DRAIN = [
    ("Heritage Damage", ["heritage", "historic"]),
    ("Heat Hazard", [
        "heatwave", "heat wave", "sunstroke", "extreme heat", "heat hazard",
        "°c", "temperature", "melting", "burns", "storing heat", "unbearable heat",
    ]),
    ("Flooding", ["flood", "waterlog", "water-log", "water logging"]),
]
CATEGORY_RULES_AFTER_DRAIN = [
    ("Pothole", ["pothole"]),
    ("Streetlight", [
        "streetlight", "street light", "lights out", "light out", "flicker",
        "spark", "unlit",
    ]),
    ("Waste", ["garbage", "waste", "dumped", "dustbin", "dead animal", "bulk waste", "bins"]),
    ("Noise", ["noise", "music", "loud", "band playing", "drilling", "amplifier"]),
    ("Road Damage", [
        "road surface", "cracked", "sinking", "footpath", "manhole", "road damage",
        "tyre damage", "subsided", "subsidence", "collapsed", "crater", "paving",
    ]),
]

# Per agents.md: priority must be Urgent if any of these appear in the description.
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def _find_matches(text: str, keywords: list) -> list:
    lower = text.lower()
    return [kw for kw in keywords if kw in lower]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category = "Other"
    matched_category_words = []

    for cat, keywords in CATEGORY_RULES_BEFORE_DRAIN:
        hits = _find_matches(description, keywords)
        if hits:
            category = cat
            matched_category_words = hits
            break

    if category == "Other":
        lower_desc = description.lower()
        if "drain" in lower_desc and "block" in lower_desc:
            category = "Drain Blockage"
            matched_category_words = ["drain", "block"]

    if category == "Other":
        for cat, keywords in CATEGORY_RULES_AFTER_DRAIN:
            hits = _find_matches(description, keywords)
            if hits:
                category = cat
                matched_category_words = hits
                break

    urgent_hits = _find_matches(description, URGENT_KEYWORDS)
    priority = "Urgent" if urgent_hits else "Standard"

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    reason_parts = []
    if matched_category_words:
        reason_parts.append(f"Matched '{matched_category_words[0]}' → {category}.")
    else:
        reason_parts.append("No category keyword matched description.")
    if urgent_hits:
        reason_parts.append(f"Severity keyword '{urgent_hits[0]}' found → Urgent.")
    reason = " ".join(reason_parts)

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never crashes on a bad row — a row missing 'description' is classified
    as Other/NEEDS_REVIEW rather than skipped.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames or [])
        for extra in ("category", "priority", "reason", "flag"):
            if extra not in fieldnames:
                fieldnames.append(extra)

        rows_out = []
        for row in reader:
            result = classify_complaint(row)
            row.update(result)
            rows_out.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
