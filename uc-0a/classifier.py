"""
UC-0A — Complaint Classifier
Classifies citizen complaints into category, priority, reason, and flag
following the fixed schema in agents.md / skills.md. Implements the two
skills: classify_complaint, batch_classify.
"""

import argparse
import csv
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword -> category signal. Order matters: first match wins unless
# multiple distinct categories are signalled, in which case we flag ambiguity.
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole"],
    "Flooding": ["flood", "waterlogg", "water logging"],
    "Streetlight": ["streetlight", "street light", "lamp post", "lamppost"],
    "Waste": ["garbage", "trash", "waste", "litter", "dumping"],
    "Noise": ["noise", "loud", "honking", "disturbance"],
    "Road Damage": ["road damage", "cracked road", "broken road", "road crack"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    "Heat Hazard": ["heat", "sunstroke", "heatstroke", "overheat"],
    "Drain Blockage": ["drain", "sewage", "clogged drain", "blocked drain"],
}


def classify_complaint(row):
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Category detection ---
    matched_categories = []
    matched_words = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                matched_words[category] = kw
                break

    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        cat_reason_word = matched_words[category]
    elif len(matched_categories) > 1:
        # Genuinely ambiguous between two+ categories
        category = "Other"
        flag = "NEEDS_REVIEW"
        cat_reason_word = " / ".join(matched_words[c] for c in matched_categories)
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cat_reason_word = None

    # --- Severity / priority detection (independent of category) ---
    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if found_severity:
        priority = "Urgent"
    else:
        # Simple heuristic for Standard vs Low when not urgent
        priority = "Standard" if len(description) > 40 else "Low"

    # --- Reason construction, citing specific words ---
    reason_parts = []
    if cat_reason_word:
        reason_parts.append(f"description mentions '{cat_reason_word}'")
    if found_severity:
        reason_parts.append(f"severity keyword(s) found: {', '.join(found_severity)}")
    if not reason_parts:
        reason_parts.append("no matching category or severity keywords found in description")

    reason = "; ".join(reason_parts)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path, output_path):
    try:
        with open(input_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as e:
            result = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": f"Processing error: {e}",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    results = batch_classify(args.input, args.output)
    print(f"Done. Classified {len(results)} row(s). Results written to {args.output}")
