"""
UC-0A — Complaint Classifier
Classifies civic complaints by category and priority using keyword rules.
CRAFT-enforced: taxonomy fixed, severity keywords explicit, reason cites description.
"""
import argparse
import csv

# Fixed allowed categories — no variations permitted
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that MUST trigger Urgent priority
URGENT_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "fallen", "collapse",
    "collapsed", "risk", "sparking", "stranded", "missing cover", "elderly", "danger"
]

# Category keyword mapping — order matters (first match wins)
CATEGORY_RULES = [
    ("Pothole",         ["pothole", "pot hole"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlogged", "knee-deep", "inundated"]),
    ("Drain Blockage",  ["drain", "drainage", "blocked drain", "drain blocked", "manhole"]),
    ("Streetlight",     ["streetlight", "street light", "light out", "lights out",
                         "flickering", "sparking", "lamp", "lighting"]),
    ("Waste",           ["garbage", "waste", "rubbish", "dump", "dumped", "bins",
                         "overflowing", "dead animal", "litter"]),
    ("Noise",           ["noise", "music", "loud", "midnight", "sound"]),
    ("Road Damage",     ["road surface", "cracked", "sinking", "broken", "footpath",
                         "tiles broken", "upturned", "road damage"]),
    ("Heritage Damage", ["heritage", "heritage street", "heritage building"]),
    ("Heat Hazard",     ["heat", "temperature", "sun", "heat hazard"]),
]


def detect_category(description: str) -> tuple[str, str]:
    """
    Returns (category, flag).
    Matches description against category rules.
    Falls back to Other + NEEDS_REVIEW if ambiguous.
    """
    desc_lower = description.lower()
    matches = []

    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                matches.append(category)
                break  # one match per category is enough

    if len(matches) == 1:
        return matches[0], ""
    elif len(matches) > 1:
        # Multiple categories match — pick the first, flag for review
        return matches[0], "NEEDS_REVIEW"
    else:
        return "Other", "NEEDS_REVIEW"


def detect_priority(description: str) -> tuple[str, str]:
    """
    Returns (priority, matched_keyword).
    Urgent if any severity keyword found. Standard otherwise.
    """
    desc_lower = description.lower()
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            return "Urgent", kw
    return "Standard", ""


def build_reason(description: str, category: str, priority: str, keyword: str) -> str:
    """
    Builds a reason sentence that cites specific words from the description.
    """
    # Extract a short excerpt from description (first 80 chars)
    excerpt = description[:80].rstrip()
    if priority == "Urgent" and keyword:
        return f"Description mentions '{keyword}' — '{excerpt}...' — classified as {category} with Urgent priority."
    else:
        return f"Description states '{excerpt}...' — classified as {category}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Handle null/empty description
    if not description or str(description).strip() == "":
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided — cannot classify.",
            "flag": "NEEDS_REVIEW"
        }

    description = str(description).strip()

    category, flag = detect_category(description)
    priority, matched_kw = detect_priority(description)
    reason = build_reason(description, category, priority, matched_kw)

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
    Reports null descriptions before processing.
    Never crashes on bad rows.
    """
    rows = []
    null_rows = []

    # Read input
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Null report — printed before any classification
    for row in rows:
        desc = row.get("description", "")
        if not desc or str(desc).strip() == "":
            null_rows.append(row.get("complaint_id", "UNKNOWN"))

    if null_rows:
        print(f"NULL REPORT: {len(null_rows)} row(s) have empty description: {null_rows}")
    else:
        print(f"NULL REPORT: No null descriptions found. All {len(rows)} rows have descriptions.")

    # Classify each row
    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as e:
            result = {
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            }
        results.append(result)

    # Write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    urgent_count = sum(1 for r in results if r["priority"] == "Urgent")
    review_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"Classified {len(results)} complaints: {urgent_count} Urgent, {review_count} flagged NEEDS_REVIEW.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")