"""
UC-0A — Complaint Classifier

Classifies each complaint row into category, priority, reason, and flag
using only that row's own description text. Refuses to guess a specific
category when the description genuinely matches more than one category
(or none), and only assigns Urgent priority when a defined severity
keyword is actually present in the text.
"""
import argparse
import csv

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out", "flicker", "spark"],
    "Waste": ["garbage", "waste", "trash", "dumped", "dead animal", "bin"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath", "tiles", "manhole", "road damage"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat wave", "heatstroke", "extreme heat", "heat hazard"],
    "Drain Blockage": ["drain blocked", "drain blockage", "clogged drain", "drain"],
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description") or ""
    desc_lower = description.lower()

    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description was empty or missing, so no category could be determined from the text.",
            "flag": "NEEDS_REVIEW",
        }

    matched = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in desc_lower]
        if hits:
            matched[category] = hits

    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]

    if len(matched) == 1:
        category = next(iter(matched))
        hits = matched[category]
        flag = ""
        reason_core = f"classified as {category} based on the word(s) '{', '.join(hits)}' in the description"
    elif len(matched) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_core = "no recognizable category keywords were found in the description, so it cannot be confidently classified"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        matched_list = ", ".join(matched.keys())
        reason_core = f"the description matches more than one category ({matched_list}) and is genuinely ambiguous"

    if severity_hits:
        priority = "Urgent"
        reason = f"{reason_core}; priority set to Urgent due to severity word(s) '{', '.join(severity_hits)}' in the description."
    else:
        priority = "Standard"
        reason = f"{reason_core}; no severity keywords found, so priority is Standard."

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
    Does not crash on malformed rows -- writes them as Other/NEEDS_REVIEW instead.
    """
    results = []

    with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if not row.get("complaint_id"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Row was missing a complaint_id and could not be reliably processed.",
                        "flag": "NEEDS_REVIEW",
                    })
                    continue
                results.append(classify_complaint(row))
            except Exception as exc:
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be processed due to an unexpected error: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
