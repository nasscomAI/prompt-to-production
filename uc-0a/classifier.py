"""
UC-0A — Complaint Classifier
Keyword-based classifier enforcing the rules defined in agents.md.
"""
import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Ordered from most specific to least specific.
# First matching rule wins the primary category; if a second rule also
# matches, flag=NEEDS_REVIEW is set.
CATEGORY_RULES = [
    ("Heritage Damage",  ["heritage", "monument", "historical building", "ancient structure"]),
    ("Drain Blockage",   ["drain block", "blocked drain", "drain clog", "drain choked"]),
    ("Heat Hazard",      ["heat hazard", "extreme heat", "heat stroke", "heat wave"]),
    ("Flooding",         ["flood", "flooded", "flooding", "waterlog", "submerged",
                          "standing in water", "knee-deep", "inundat"]),
    ("Streetlight",      ["streetlight", "street light", "street lamp",
                          "lights out", "light out", "sparking", "light flicker",
                          "flickering"]),
    ("Pothole",          ["pothole", "pot hole", "pot-hole"]),
    ("Noise",            ["noise", "music", "loud", "blaring"]),
    ("Waste",            ["garbage", "waste", "dead animal", "rubbish",
                          "overflowing bin", "dumped on", "dump"]),
    ("Road Damage",      ["manhole", "footpath", "road surface", "road crack",
                          "cracked", "sinking", "upturned", "tiles broken",
                          "tile broken", "road damage"]),
]

ALLOWED_CATEGORIES = {r[0] for r in CATEGORY_RULES} | {"Other"}


def _find_severity_hit(description: str) -> str:
    """Return the first severity keyword found, or empty string."""
    low = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in low:
            return kw
    return ""


def _find_categories(description: str) -> list[str]:
    """Return list of matching categories (in rule order)."""
    low = description.lower()
    matched = []
    for category, keywords in CATEGORY_RULES:
        if any(kw in low for kw in keywords):
            matched.append(category)
    return matched


def _build_reason(description: str, category: str, severity_hit: str) -> str:
    """Construct a reason that quotes specific words from the description."""
    low = description.lower()
    # Find the keyword that drove the category choice
    category_kw = ""
    for cat, keywords in CATEGORY_RULES:
        if cat == category:
            for kw in keywords:
                if kw in low:
                    category_kw = kw
                    break
            break

    parts = []
    if category_kw:
        parts.append(f'"{category_kw}" in description')
    if severity_hit:
        parts.append(f'severity keyword "{severity_hit}" triggers Urgent')

    if parts:
        return "; ".join(parts)
    return f'Classified as {category} based on complaint description'


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with all original keys plus: category, priority, reason, flag.
    """
    description = (row.get("description") or "").strip()

    if not description:
        return {
            **row,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    matched_categories = _find_categories(description)
    severity_hit = _find_severity_hit(description)

    if not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        # Multiple matches — pick the first (most specific per rule order)
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"

    priority = "Urgent" if severity_hit else "Standard"
    reason = _build_reason(description, category, severity_hit)

    return {
        **row,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Prints a summary to stdout on completion.
    """
    results = []
    errors = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        input_fieldnames = reader.fieldnames or []
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as e:
                errors.append((row.get("complaint_id", "?"), str(e)))
                results.append({
                    **row,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {e}",
                    "flag": "NEEDS_REVIEW",
                })

    output_fieldnames = list(input_fieldnames) + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(results)

    urgent_count = sum(1 for r in results if r.get("priority") == "Urgent")
    review_count = sum(1 for r in results if r.get("flag") == "NEEDS_REVIEW")

    print(f"Classified {len(results)} complaints → {output_path}")
    print(f"  Urgent:       {urgent_count}")
    print(f"  NEEDS_REVIEW: {review_count}")
    if errors:
        print(f"  Errors ({len(errors)}):")
        for cid, msg in errors:
            print(f"    {cid}: {msg}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
