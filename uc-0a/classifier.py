"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.
"""
import argparse
import csv
import os

# --- Schema (agents.md enforcement rule 1) ---
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# agents.md enforcement rule 2
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword → category mapping (most specific patterns first)
CATEGORY_KEYWORDS = [
    ("Pothole",         ["pothole", "pot hole"]),
    ("Flooding",        ["flood", "waterlog", "waterlogged", "inundat", "overflow"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "unlit", "no light", "lighting", "lamp"]),
    ("Waste",           ["garbage", "waste", "trash", "rubbish", "litter", "dump", "refuse", "sanitation"]),
    ("Noise",           ["noise", "loud", "honking", "disturbance", "nuisance"]),
    ("Heat Hazard",     ["melting", "heatwave", "heat wave", "dangerous temperature", "heat", "temperature"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient", "historic"]),
    ("Drain Blockage",  ["drain", "drainage", "sewer", "blockage", "clog"]),
    ("Road Damage",     ["tarmac", "pavement", "asphalt", "road damage", "carriageway", "road crack", "road surface"]),
]


def _find_severity_triggers(description: str) -> list:
    """Return severity keywords present in description (case-insensitive)."""
    desc_lower = description.lower()
    return [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]


def _find_category(description: str):
    """
    Return (category, matched_keyword) via keyword matching.
    Returns ("Other", None) when no category matches.
    """
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in desc_lower:
                return category, kw
    return "Other", None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Input:  dict with at minimum a `description` string field (skills.md).
    Output: dict with category, priority, reason, flag (skills.md).
    """
    description = (row.get("description") or "").strip()

    # skills.md error_handling: empty / missing description
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    # agents.md enforcement rule 2: severity keywords → Urgent
    severity_triggers = _find_severity_triggers(description)
    priority = "Urgent" if severity_triggers else "Standard"

    # agents.md enforcement rule 1: exact category from allowed list
    category, matched_kw = _find_category(description)

    # agents.md enforcement rules 3 & 4: reason + flag
    if category == "Other":
        flag = "NEEDS_REVIEW"
        snippet = description[:70] + ("..." if len(description) > 70 else "")
        reason = f"Description '{snippet}' does not clearly match any allowed category."
    else:
        flag = ""
        severity_note = (
            f" Severity keyword '{severity_triggers[0]}' triggers Urgent priority."
            if severity_triggers else ""
        )
        # agents.md enforcement rule 3: cite specific words from description
        reason = f"Description contains '{matched_kw}', indicating {category}.{severity_note}"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Input:  paths to input and output CSV files (skills.md).
    Output: output CSV with original columns + category, priority, reason, flag appended.
    Error handling per skills.md:
      - raises FileNotFoundError if input missing
      - on per-row failure writes Other + NEEDS_REVIEW and continues
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        original_fields = list(reader.fieldnames or [])
        rows = list(reader)

    output_fields = original_fields + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Classification failed for this row.",
                    "flag": "NEEDS_REVIEW",
                }
            row.update(result)
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
