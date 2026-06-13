"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Ordered so more specific patterns are checked before broad ones
CATEGORY_KEYWORDS = [
    ("Heritage Damage", ["heritage"]),
    ("Pothole",         ["pothole"]),
    ("Drain Blockage",  ["drain blocked", "drain", "manhole"]),
    ("Flooding",        ["flood", "flooded", "flooding"]),
    ("Streetlight",     ["streetlight", "street light", "street-light", "lights out", "light out", "sparking", "lamp"]),
    ("Waste",           ["garbage", "overflowing", "dead animal", "waste dumped", "bulk waste", "rubbish"]),
    ("Noise",           ["music past midnight", "noise", "loud music"]),
    ("Road Damage",     ["road surface", "cracked", "sinking", "footpath", "tiles broken", "tiles upturned", "upturned"]),
    ("Heat Hazard",     ["heat", "temperature"]),
]


def classify_complaint(row: dict) -> dict:
    """Classify one complaint row; always returns a complete result dict."""
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Priority: Urgent if any severity keyword present
    triggered = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    priority = "Urgent" if triggered else "Standard"

    # Category: first matching rule wins
    matched_category = None
    matched_keyword = None
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in desc_lower:
                matched_category = category
                matched_keyword = kw
                break
        if matched_category:
            break

    flag = ""
    if matched_category is None:
        matched_category = "Other"
        flag = "NEEDS_REVIEW"

    # Reason must cite words from the description
    if matched_keyword:
        reason = f'Classified as {matched_category} based on "{matched_keyword}" in description.'
    else:
        reason = "No matching category keyword found in description."
        flag = "NEEDS_REVIEW"

    if triggered:
        kw_list = ", ".join(f'"{k}"' for k in triggered)
        reason += f" Priority Urgent: severity keyword(s) {kw_list} detected."

    return {
        "complaint_id": complaint_id,
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify every row, write results CSV. Never skips rows silently."""
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    for row in rows:
        required = {"complaint_id", "description"}
        if not required.issubset(row.keys()):
            results.append({
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": "Missing required fields.",
                "flag": "NEEDS_REVIEW",
            })
            continue
        try:
            results.append(classify_complaint(row))
        except Exception as exc:
            results.append({
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {exc}",
                "flag": "NEEDS_REVIEW",
            })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
