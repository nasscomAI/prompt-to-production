"""
UC-0A — Complaint Classifier
Built per agents.md (RICE enforcement rules) and skills.md.
"""
import argparse
import csv
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse",
]

# (category, keywords) — checked in order; first match wins. Order matters: more specific
# categories (Drain Blockage) are checked before their broader neighbour (Flooding) so a
# "drain blocked, road flooded" complaint doesn't silently collapse into the wrong bucket.
CATEGORY_RULES = [
    ("Pothole", ["pothole"]),
    ("Drain Blockage", ["drain block", "blocked drain", "drain clog"]),
    ("Flooding", ["flood", "waterlog", "water logging", "knee-deep", "stranded"]),
    ("Streetlight", ["streetlight", "street light", "street lamp"]),
    ("Waste", ["garbage", "waste", "trash", "dump", "littering", "dead animal", "carcass", "not removed"]),
    ("Noise", ["noise", "loud", "honking", "music", "midnight", "wedding venue"]),
    ("Heritage Damage", ["heritage", "monument", "historic"]),
    ("Heat Hazard", ["heat wave", "heatwave", "heat hazard", "extreme heat"]),
    ("Road Damage", [
        "road damage", "crack", "collapse", "caved", "cave-in", "sinking road",
        "manhole", "footpath", "tiles broken", "upturned",
    ]),
]


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
            "reason": "description missing",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- category: first matching rule wins ---
    category = None
    matched_phrase = None
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                matched_phrase = kw
                break
        if category:
            break

    flag = ""
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"
        matched_phrase = None

    # --- priority: severity keyword overrides everything ---
    hit_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if hit_severity:
        priority = "Urgent"
        reason = f"Urgent: description contains severity keyword(s) {', '.join(hit_severity)}."
    elif category == "Other":
        priority = "Standard"
        reason = "No category keyword matched description; flagged for manual review."
    else:
        priority = "Standard"
        reason = f"Classified as {category} based on keyword '{matched_phrase}' in description."

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
    Never aborts the whole batch on a single bad row.
    """
    results = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                results.append(classify_complaint(row))
            except Exception as exc:  # noqa: BLE001 — must not crash the batch on one bad row
                print(f"WARN: row {i} ({row.get('complaint_id', '?')}) failed: {exc}", file=sys.stderr)
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"classification error: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
