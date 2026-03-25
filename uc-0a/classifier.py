"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.
"""
import argparse
import csv
import re

# ── Schema constants ──────────────────────────────────────────────────────────
# agents.md enforcement rule 1: exact allowed category strings
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# agents.md enforcement rule 2: severity keywords that must trigger Urgent
URGENT_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
}

# Category keyword map — ordered most-specific first to avoid false matches
CATEGORY_RULES = [
    ("Heritage Damage", ["heritage", "monument", "historical", "historic",
                         "ancient", "temple", "statue", "graffiti"]),
    ("Heat Hazard",     ["heat", "hot", "overheating", "thermal",
                         "burnt", "burning", "temperature"]),
    ("Drain Blockage",  ["drain", "drainage", "sewer", "manhole",
                         "gutter", "clogged"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlog",
                         "waterlogged", "inundated", "standing water", "overflow"]),
    ("Streetlight",     ["streetlight", "street light", "lamp", "lamppost",
                         "lighting", "light out", "dark", "darkness", "bulb"]),
    ("Pothole",         ["pothole", "pot hole", "pit", "crater",
                         "dip", "sinkhole"]),
    ("Road Damage",     ["road damage", "cracked road", "broken road",
                         "asphalt", "tarmac", "pavement damage", "road surface",
                         "crack"]),
    ("Waste",           ["garbage", "waste", "trash", "rubbish", "litter",
                         "dumping", "dump", "debris", "sewage", "refuse"]),
    ("Noise",           ["noise", "loud", "blaring", "horn", "drilling",
                         "disturbance", "music"]),
]


def _detect_category(description: str) -> tuple[str, str]:
    """Return (category, matched_keyword); ('Other', '') if nothing matches."""
    text = description.lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return category, kw
    return "Other", ""


def _detect_priority(description: str) -> tuple[str, str]:
    """Return (priority, matched_keyword). Urgent takes precedence."""
    words = re.findall(r"\b\w+\b", description.lower())
    for word in words:
        if word in URGENT_KEYWORDS:
            return "Urgent", word
    # Non-urgent: Standard for substantive descriptions, Low for brief ones
    if len(description.strip()) > 30:
        return "Standard", ""
    return "Low", ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row (skills.md: classify_complaint).

    Input:  dict with 'complaint_id' (str) and 'description' (str).
    Output: dict with keys: complaint_id, category, priority, reason, flag.

    Never raises — missing/empty description returns a safe NEEDS_REVIEW result
    so batch_classify is never interrupted.
    """
    complaint_id = row.get("complaint_id", "")
    description  = (row.get("description") or "").strip()

    # skills.md error_handling: missing or empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description was empty or missing.",
            "flag":         "NEEDS_REVIEW",
        }

    category, cat_kw = _detect_category(description)
    priority, urg_kw = _detect_priority(description)

    # agents.md enforcement rule 4: ambiguous → Other + NEEDS_REVIEW
    if category == "Other":
        snippet = description[:80]
        reason  = f"Description '{snippet}' did not match any known category."
        flag    = "NEEDS_REVIEW"
    else:
        # agents.md enforcement rule 3: reason must cite description words
        if urg_kw:
            reason = (
                f"Classified as {category} based on '{cat_kw}' in the description; "
                f"priority set to Urgent due to '{urg_kw}'."
            )
        else:
            reason = f"Classified as {category} based on '{cat_kw}' in the description."
        flag = ""

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


OUTPUT_FIELDNAMES = ["complaint_id", "category", "priority", "reason", "flag"]


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify every row, write results CSV (skills.md: batch_classify).

    Raises FileNotFoundError if input_path cannot be opened.
    Malformed rows are written with category: Other and flag: NEEDS_REVIEW;
    processing continues for all remaining rows.
    """
    try:
        input_file = open(input_path, newline="", encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with input_file:
        reader = csv.DictReader(input_file)
        for i, row in enumerate(reader):
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": row.get("complaint_id", f"row_{i}"),
                    "category":     "Other",
                    "priority":     "Low",
                    "reason":       f"Row could not be parsed: {exc}",
                    "flag":         "NEEDS_REVIEW",
                }
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
