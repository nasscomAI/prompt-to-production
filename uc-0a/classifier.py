"""
UC-0A — Complaint Classifier
Built using the RICE (Role, Intent, Context, Enforcement) -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse", "collapsed",
]

# Ordered: first match wins. Order matters because some descriptions
# contain overlapping words (e.g. a flooded street may also mention a drain).
CATEGORY_RULES = [
    ("Heritage Damage", ["heritage", "monument", "historic"]),
    ("Heat Hazard", ["heat wave", "heatstroke", "sunstroke", "heat hazard"]),
    ("Pothole", ["pothole", "pot hole"]),
    ("Flooding", ["flood", "flooded", "waterlogg", "knee-deep", "stranded"]),
    ("Drain Blockage", ["drain block", "blocked drain", "drain clog", "drain overflow"]),
    ("Streetlight", ["streetlight", "street light", "lamp post", "lamppost"]),
    ("Waste", ["garbage", "waste", "trash", "dump", "litter"]),
    ("Noise", ["noise", "loud", "blaring", "construction at night", "music", "midnight", "loudspeaker"]),
    ("Road Damage", ["road damage", "crack", "caved", "sunk", "road caved"]),
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = (row.get("description") or "").strip()
    desc_lower = description.lower()

    # --- category ---
    category = "Other"
    matched_category_words = []
    for cat_name, keywords in CATEGORY_RULES:
        hits = [kw for kw in keywords if kw in desc_lower]
        if hits:
            category = cat_name
            matched_category_words = hits
            break

    # --- priority ---
    matched_severity_words = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if matched_severity_words:
        priority = "Urgent"
    elif "minor" in desc_lower or "cosmetic" in desc_lower:
        priority = "Low"
    else:
        priority = "Standard"

    # --- flag ---
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    # --- reason (must cite specific words from the description) ---
    if matched_severity_words and matched_category_words:
        reason = (
            f"Classified as {category} (keyword: '{matched_category_words[0]}') "
            f"and marked {priority} due to severity term(s): "
            f"{', '.join(matched_severity_words)}."
        )
    elif matched_category_words:
        reason = (
            f"Classified as {category} based on keyword '{matched_category_words[0]}' "
            f"in the description; no severity terms present, so priority is {priority}."
        )
    else:
        reason = (
            "No category keyword matched the description confidently; "
            "flagged for manual review rather than guessing."
        )

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
    Never crashes on a single bad row — bad rows are flagged NEEDS_REVIEW instead.
    """
    with open(input_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    fieldnames = ["complaint_id", "ward", "description", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception as e:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be processed automatically ({e}); needs manual review.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow({
                "complaint_id": result["complaint_id"],
                "ward": row.get("ward", ""),
                "description": row.get("description", ""),
                "category": result["category"],
                "priority": result["priority"],
                "reason": result["reason"],
                "flag": result["flag"],
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")