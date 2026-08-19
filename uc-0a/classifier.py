"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md (RICE) and skills.md.
"""
import argparse
import csv
import sys

# --- Enforcement constants from agents.md ---

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}

# Maps description keywords to categories (order matters — first match wins)
CATEGORY_KEYWORDS = [
    ("Pothole",         ["pothole", "pot hole", "pot-hole"]),
    ("Flooding",        ["flood", "waterlog", "water log", "water-log", "inundated", "submerged",
                         "water overflow", "drain overflow", "road overflow"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "lamppost", "light out", "no light", "dark street"]),
    ("Waste",           ["garbage", "waste", "rubbish", "litter", "dump", "trash", "filth", "sewage", "smell",
                         "overflowing bin", "overflowing garbage", "dead animal", "animal carcass", "carcass",
                         "animal not removed", "health concern"]),
    ("Noise",           ["noise", "loud", "sound", "music", "construction noise", "horn"]),
    ("Road Damage",     ["road damage", "damaged road", "broken road", "cracked road", "road crack", "road broken",
                         "road surface", "surface cracked", "road sinking", "sinking road", "road collapsed"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient", "temple wall", "fort"]),
    ("Heat Hazard",     ["heat", "hot", "temperature", "heatwave", "heat wave", "scorching"]),
    ("Drain Blockage",  ["drain", "blocked drain", "drain block", "clogged", "manhole", "sewer block"]),
]


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Returns (category, is_ambiguous).
    Matches against CATEGORY_KEYWORDS in priority order.
    Falls back to Other + ambiguous=True if no match found.
    """
    text = description.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        if any(kw in text for kw in keywords):
            return category, False
    return "Other", True


def _detect_priority(description: str) -> str:
    """Returns Urgent if any severity keyword is present, else Standard."""
    text = description.lower()
    if any(kw in text for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Builds a one-sentence reason quoting specific words from the description.
    """
    text_lower = description.lower()

    # Find the category-triggering keyword(s)
    cat_triggers = []
    for cat, keywords in CATEGORY_KEYWORDS:
        if cat == category:
            cat_triggers = [kw for kw in keywords if kw in text_lower]
            break

    # Find the severity-triggering keyword(s)
    sev_triggers = [kw for kw in SEVERITY_KEYWORDS if kw in text_lower]

    parts = []
    if cat_triggers:
        parts.append(f"description contains '{cat_triggers[0]}' indicating {category}")
    elif category == "Other":
        parts.append("no matching category keywords found")

    if sev_triggers:
        parts.append(f"severity keyword '{sev_triggers[0]}' triggers Urgent priority")

    if parts:
        return "Classified as " + " and ".join(parts) + "."
    return f"Classified based on description content as {category} with {priority} priority."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag.
    Enforces all rules from agents.md.
    """
    description = (row.get("description") or "").strip()
    complaint_id = row.get("id", row.get("complaint_id", ""))

    # Error path: empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Standard",
            "reason":       "No description provided — cannot classify.",
            "flag":         "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    priority = _detect_priority(description)
    reason = _build_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Appends: category, priority, reason, flag columns.
    Prints summary to stdout.
    """
    # Validate input file exists
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames or []
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Validate required columns
    required = {"id", "description"}
    # Accept complaint_id as alias for id
    present = set(fieldnames)
    if "complaint_id" in present and "id" not in present:
        present.add("id")
    missing = required - present
    if missing:
        print(f"ERROR: Missing required column(s): {', '.join(sorted(missing))}", file=sys.stderr)
        sys.exit(1)

    results = []
    needs_review_count = 0

    for row in rows:
        result = classify_complaint(row)
        if result["flag"] == "NEEDS_REVIEW":
            needs_review_count += 1
        # Merge original row with classification output
        merged = dict(row)
        merged["category"] = result["category"]
        merged["priority"] = result["priority"]
        merged["reason"]   = result["reason"]
        merged["flag"]     = result["flag"]
        results.append(merged)

    # Write output CSV
    out_fieldnames = list(fieldnames) + [
        f for f in ["category", "priority", "reason", "flag"]
        if f not in fieldnames
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} rows. NEEDS_REVIEW: {needs_review_count}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
