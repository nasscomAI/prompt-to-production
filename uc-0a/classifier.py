"""
UC-0A — Complaint Classifier
Built via RICE prompt -> agents.md -> skills.md -> CRAFT loop.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "flooded", "knee-deep", "water logging", "waterlogging"]),
    ("Streetlight", ["streetlight", "street light", "flickering", "sparking", "light"]),
    ("Waste", ["garbage", "waste", "dumped", "dead animal", "bins"]),
    ("Noise", ["music", "noise", "loud"]),
    ("Heritage Damage", ["heritage"]),
    ("Drain Blockage", ["drain blocked", "drainage", "drain"]),
    ("Road Damage", ["cracked", "sinking", "manhole", "footpath", "tiles", "bridge"]),
    ("Heat Hazard", ["heat", "heatwave"]),
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()
    desc_lower = description.lower()

    if len(description.split()) < 5:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Insufficient description to classify",
            "flag": "NEEDS_REVIEW",
        }

    matched_categories = []
    matched_keyword = None
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                if matched_keyword is None:
                    matched_keyword = kw
                break

    seen = set()
    matched_categories = [c for c in matched_categories if not (c in seen or seen.add(c))]

    if not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_evidence = description[:40]
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        reason_evidence = matched_keyword
    else:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
        reason_evidence = matched_keyword

    severity_hit = next((kw for kw in SEVERITY_KEYWORDS if kw in desc_lower), None)
    priority = "Urgent" if severity_hit else "Standard"

    if severity_hit:
        reason = f'Contains severity keyword "{severity_hit}" and matched "{reason_evidence}" -> {category}, Urgent.'
    elif category == "Other":
        reason = f'No matching category keywords found in description ("{reason_evidence}...") -> Other, flagged for review.'
    else:
        reason = f'Matched keyword "{reason_evidence}" -> {category}, no severity keyword found.'

    if len(matched_categories) > 1 and flag == "NEEDS_REVIEW":
        reason = f'Description supports multiple categories ({", ".join(matched_categories)}); best match "{category}" via "{reason_evidence}" -> flagged for review.'

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
    """
    with open(input_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            if not row.get("description"):
                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Description column missing or empty",
                    "flag": "NEEDS_REVIEW",
                })
                continue
            writer.writerow(classify_complaint(row))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
