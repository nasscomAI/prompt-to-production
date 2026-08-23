"""
UC-0A — Complaint Classifier
Deterministic municipal complaint classifier implementing the contracts
defined in agents.md and skills.md.
"""
import argparse
import csv
import sys

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

LOW_KEYWORDS = ["cosmetic", "aesthetic", "paint", "faded", "minor"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out"],
    "Waste": ["garbage", "waste", "trash", "litter", "rubbish", "dead animal", "dump"],
    "Noise": ["noise", "loud", "music"],
    "Road Damage": ["crack", "sink", "broken", "footpath", "manhole", "tile"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "heatwave"],
    "Drain Blockage": [
        "drain block", "blocked drain", "drainage block",
        "clogged drain", "drain overflow", "overflowing drain",
    ],
}

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _quote(words):
    return ", ".join(f'"{w}"' for w in words)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    Never raises; falls back to Other / Standard / NEEDS_REVIEW.
    """
    row = row or {}
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    description = (row.get("description") or "").strip()
    text = description.lower()

    if not text:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided, so no category could be determined.",
            "flag": "NEEDS_REVIEW",
        }

    hits = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        found = [kw for kw in keywords if kw in text]
        if found:
            hits[category] = found

    if len(hits) == 1:
        category = next(iter(hits))
        flag = ""
        head = f"classified as {category} because the description cites {_quote(hits[category])}"
    elif hits:
        names = " and ".join(sorted(hits))
        all_keywords = sorted({kw for kws in hits.values() for kw in kws})
        category = "Other"
        flag = "NEEDS_REVIEW"
        head = f"ambiguous between {names} because the description cites {_quote(all_keywords)}"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        head = "no allowed category fits the description"

    urgent_hit = next((kw for kw in URGENT_KEYWORDS if kw in text), None)
    if urgent_hit:
        priority = "Urgent"
        tail = f'urgent keywords present ("{urgent_hit}")'
    elif any(kw in text for kw in LOW_KEYWORDS):
        priority = "Low"
        tail = "issue appears cosmetic or non-disruptive"
    else:
        priority = "Standard"
        tail = "no urgent keywords present"

    reason = f"{head.capitalize()}; {tail}."
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> int:
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        infile = open(input_path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        print(f"Error: cannot read input file '{input_path}': {exc}", file=sys.stderr)
        return 1

    total = classified = flagged = 0
    with infile, open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in reader:
            total += 1
            if row.get(None) or any(value is None for value in row.values()):
                label = (row.get("complaint_id") or f"line {reader.line_num}")
                print(f"Warning: malformed CSV row ({label}); applying fallback.",
                      file=sys.stderr)
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": (row or {}).get("complaint_id") or "UNKNOWN",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed internally ({exc}).",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)
            classified += 1
            if result["flag"] == "NEEDS_REVIEW":
                flagged += 1

    print(f"Summary: {total} rows read, {classified} classified, "
          f"{flagged} flagged NEEDS_REVIEW.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    rc = batch_classify(args.input, args.output)
    if rc == 0:
        print(f"Done. Results written to {args.output}")
    sys.exit(rc)
