"""
UC-0A – Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "underpass", "waterlog"],
    "Streetlight": ["streetlight", "street light", "flickering", "dark at night"],
    "Waste": ["garbage", "waste", "dumped", "trash", "bins"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath", "tiles broken"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "heatwave"],
    "Drain Blockage": ["drain blocked", "drain blockage", "manhole"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Category detection ---
    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            matched_categories.append(category)

    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cat_part = "no matching category keywords found"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        reason_cat_part = f"matched keyword for {category.lower()}"
    else:
        # Ambiguous: fits more than one category
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
        reason_cat_part = f"description matches multiple categories ({', '.join(matched_categories)})"

    # --- Priority detection ---
    found_urgent_keywords = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    if found_urgent_keywords:
        priority = "Urgent"
        reason_pri_part = f"severity keyword(s) found: {', '.join(found_urgent_keywords)}"
    else:
        priority = "Standard"
        reason_pri_part = "no severity keywords found"

    reason = f"{reason_cat_part}; {reason_pri_part}."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    output_rows = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as e:
            result = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {e}",
                "flag": "NEEDS_REVIEW",
            }
        merged = {**row, **result}
        output_rows.append(merged)

    fieldnames = list(rows[0].keys()) + ["category", "priority", "reason", "flag"]
    # Deduplicate fieldnames while preserving order
    seen = set()
    fieldnames = [f for f in fieldnames if not (f in seen or seen.add(f))]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")