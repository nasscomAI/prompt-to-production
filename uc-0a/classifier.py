"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md (RICE) and skills.md.
"""
import argparse
import csv
import re

# --- agents.md: context — allowed categories (exact strings only) ---
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# --- agents.md: enforcement rule 2 — severity keywords that must trigger Urgent ---
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword → category mapping (longest/most-specific phrases first)
CATEGORY_KEYWORDS = [
    ("Pothole",         ["pothole", "pot hole", "crater", "tyre damage"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlog", "water logging", "knee-deep", "submerged"]),
    ("Drain Blockage",  ["drain block", "blocked drain", "choked drain", "drain overflow", "drain clog"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "light out", "light not working", "dark road", "no light"]),
    ("Waste",           ["garbage", "waste", "litter", "trash", "rubbish", "dump", "overflowing bin", "garbage pile"]),
    ("Noise",           ["noise", "loud", "nuisance", "sound", "honking", "blaring"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient", "protected structure"]),
    ("Heat Hazard",     ["heat", "temperature", "hot surface", "burning", "heat wave", "sun stroke"]),
    ("Road Damage",     ["road damage", "broken road", "damaged road", "road crack", "road collapse",
                         "road surface", "tarmac", "asphalt", "unpaved", "road broken"]),
]


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Returns (category, is_ambiguous).
    Tries keyword matching; falls back to Other + ambiguous flag.
    """
    text = description.lower()
    matched = []
    for category, keywords in CATEGORY_KEYWORDS:
        if any(kw in text for kw in keywords):
            matched.append(category)

    if len(matched) == 1:
        return matched[0], False
    if len(matched) > 1:
        # Return first (highest-priority) match but flag for review
        return matched[0], True
    return "Other", True


def _detect_priority(description: str) -> tuple[str, list[str]]:
    """
    Returns (priority, triggered_keywords).
    Urgent if any severity keyword present; else Standard.
    """
    text = description.lower()
    triggered = [kw for kw in SEVERITY_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', text)]
    if triggered:
        return "Urgent", triggered
    return "Standard", []


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns the input dict extended with: category, priority, reason, flag.
    Enforces all rules from agents.md.
    """
    description = (row.get("description") or "").strip()

    # --- Handle missing/empty description ---
    if not description:
        return {
            **row,
            "category": "Other",
            "priority":  "Low",
            "reason":    "No description provided.",
            "flag":      "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    priority, triggered_kws = _detect_priority(description)

    # --- Build reason citing specific words from the description (enforcement rule 3) ---
    if triggered_kws and is_ambiguous:
        reason = (
            f"Description contains severity keyword(s) '{', '.join(triggered_kws)}'; "
            f"category ambiguous — matched multiple types."
        )
    elif triggered_kws:
        reason = (
            f"Classified as {category}; priority Urgent because description contains "
            f"'{', '.join(triggered_kws)}'."
        )
    elif is_ambiguous:
        reason = (
            f"Category ambiguous — description does not clearly match a single category; "
            f"flagged for review."
        )
    else:
        # Find the specific word(s) that drove the category
        text = description.lower()
        driving_kws = [
            kw for cat, kws in CATEGORY_KEYWORDS if cat == category
            for kw in kws if kw in text
        ]
        cited = driving_kws[0] if driving_kws else category.lower()
        reason = f"Classified as {category} based on '{cited}' in description."

    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        **row,
        "category": category,
        "priority":  priority,
        "reason":    reason,
        "flag":      flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row via classify_complaint, write results CSV.
    Prints a summary: total rows, Urgent count, NEEDS_REVIEW count.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "description" not in (reader.fieldnames or []):
                raise ValueError(
                    f"Input CSV is missing required column 'description'. "
                    f"Found columns: {reader.fieldnames}"
                )
            rows = list(reader)
            fieldnames = reader.fieldnames
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = [classify_complaint(row) for row in rows]

    out_fields = list(fieldnames) + [
        c for c in ["category", "priority", "reason", "flag"]
        if c not in fieldnames
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    total        = len(results)
    urgent_count = sum(1 for r in results if r.get("priority") == "Urgent")
    review_count = sum(1 for r in results if r.get("flag") == "NEEDS_REVIEW")

    print(f"Classified {total} complaint(s) — "
          f"Urgent: {urgent_count}, NEEDS_REVIEW: {review_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
