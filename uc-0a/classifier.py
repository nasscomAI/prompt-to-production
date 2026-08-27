"""
UC-0A — Complaint Classifier
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.
"""

import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole", "road hole", "crater"],
    "Flooding": ["flood", "waterlogging", "water logged", "water-logged", "inundat"],
    "Streetlight": ["streetlight", "street light", "lamp post", "lamppost", "no light", "not working"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "not collected", "dumping"],
    "Noise": ["noise", "loud", "music", "horn", "honking"],
    "Road Damage": ["road damage", "cracked road", "broken road", "road crack", "pavement"],
    "Heritage Damage": ["heritage", "monument", "old building", "historic"],
    "Heat Hazard": ["heat", "sunstroke", "heatstroke", "extreme temperature", "melting", "melted", "°c", "degrees", "dangerous temperature", "too hot"],
    "Drain Blockage": ["drain", "sewage", "blocked drain", "clogged", "overflow"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in text]
    priority = "Urgent" if matched_severity else "Standard"

    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in text]
        if hits:
            scores[category] = hits

    flag = ""
    if len(scores) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_bits = "no category keywords matched in description"
    elif len(scores) > 1:
        category = sorted(scores.keys())[0]
        flag = "NEEDS_REVIEW"
        matched_words = ", ".join(sorted({w for hits in scores.values() for w in hits}))
        reason_bits = f"multiple possible categories matched ({matched_words})"
    else:
        category = next(iter(scores))
        matched_words = ", ".join(scores[category])
        reason_bits = f"matched keyword(s): {matched_words}"

    if matched_severity:
        reason_bits += f"; severity keyword(s) found: {', '.join(matched_severity)}"

    reason = reason_bits[0].upper() + reason_bits[1:] + "."

    if not matched_severity and category == "Other" and len(text.split()) <= 6:
        priority = "Low"

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
    Flags nulls, does not crash on bad rows, always produces output.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    for col in ["category", "priority", "reason", "flag"]:
        if col not in fieldnames:
            fieldnames.append(col)
    if "priority_flag" in fieldnames:
        fieldnames.remove("priority_flag")

    results = []
    for row in rows:
        try:
            classification = classify_complaint(row)
        except Exception as exc:
            classification = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification error: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        row.update({k: v for k, v in classification.items() if k != "complaint_id"})
        row.pop("priority_flag", None)
        results.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
