"""
UC-0A — Complaint Classifier
Built per agents.md (role/intent/context/enforcement) and skills.md
(classify_complaint, batch_classify).
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Ordered most-specific-first: Pothole/Drain Blockage must win over the more
# general Road Damage/Flooding before those broader keyword sets are checked.
CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole", "tyre damage", "tire damage"]),
    ("Drain Blockage", ["drain blocked", "blocked drain", "drainage", "clogged drain", "sewage overflow", "manhole"]),
    ("Flooding", ["flood", "flooded", "waterlogged", "water-logged", "submerged", "stranded in water"]),
    ("Streetlight", ["streetlight", "street light", "lamp post", "no light", "dark street"]),
    ("Waste", ["garbage", "waste", "trash", "dump", "litter", "overflowing bin", "dead animal"]),
    ("Noise", ["noise", "loud", "honking", "decibel", "disturbance", "music past midnight", "playing music"]),
    ("Road Damage", [
        "road damage", "cracked road", "broken road", "crumbling road", "road caved",
        "road collapse", "road surface cracked", "surface cracked", "footpath tiles broken",
        "footpath broken", "sinking",
    ]),
    ("Heritage Damage", ["heritage", "monument", "historic structure"]),
    ("Heat Hazard", ["heat wave", "heatwave", "sunstroke", "extreme heat", "heat hazard"]),
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse",
]


def _find_matches(description: str, keywords: list) -> list:
    lower = description.lower()
    matches = [kw for kw in keywords if kw in lower]
    # Drop matches that are substrings of another match (e.g. "surface cracked"
    # inside "road surface cracked") so the reason doesn't repeat itself.
    return [kw for kw in matches if not any(kw != other and kw in other for other in matches)]


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
            "priority": "Low",
            "reason": "No description provided, so category and severity cannot be determined.",
            "flag": "NEEDS_REVIEW",
        }

    category = "Other"
    matched_keywords = []
    for cat, keywords in CATEGORY_KEYWORDS:
        matches = _find_matches(description, keywords)
        if matches:
            category = cat
            matched_keywords = matches
            break

    severity_matches = _find_matches(description, SEVERITY_KEYWORDS)
    priority = "Urgent" if severity_matches else "Standard"

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = f"Description does not match any known category: \"{description[:80]}\"."
    else:
        cited = ", ".join(matched_keywords + severity_matches)
        reason = f"Description mentions {cited}, indicating a {category.lower()} complaint" + (
            " with urgent severity." if priority == "Urgent" else "."
        )

    if priority == "Standard" and category != "Other":
        light_matches = _find_matches(description, ["risk", "danger", "urgent", "emergency"])
        if light_matches and not severity_matches:
            flag = "NEEDS_REVIEW"

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
    Never crashes on a bad row — a row that raises is written back with
    flag: NEEDS_REVIEW and an explanatory reason instead of failing the batch.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        input_fields = reader.fieldnames or []
        rows = list(reader)

    output_fields = input_fields + [
        f for f in ("category", "priority", "reason", "flag") if f not in input_fields
    ]

    results = []
    for row in rows:
        try:
            classification = classify_complaint(row)
        except Exception as exc:
            classification = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        merged = dict(row)
        merged["category"] = classification["category"]
        merged["priority"] = classification["priority"]
        merged["reason"] = classification["reason"]
        merged["flag"] = classification["flag"]
        results.append(merged)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
