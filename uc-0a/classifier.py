import argparse
import csv
import re

CATEGORY_RULES = [
    ("Pothole",          ["pothole"]),
    ("Flooding",         ["flood", "flooded", "waterlogging", "submerged"]),
    ("Streetlight",      ["streetlight", "lights out", "light out", "flickering", "sparking", "unlit"]),
    ("Drain Blockage",   ["drain blocked", "blocked drain", "manhole", "sewer"]),
    ("Waste",            ["garbage", "waste", "bin", "dead animal", "dumping", "overflowing", "smell"]),
    ("Heritage Damage",  ["heritage", "historic"]),
    ("Heat Hazard",      ["heat", "hot", "temperature"]),
    ("Noise",            ["noise", "music", "band", "wedding", "loud"]),
    ("Road Damage",      ["road surface", "cracked", "sinking", "broken", "footpath", "tiles", "collapsed", "subsided", "crater"]),
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]


def _word_at_start(kw: str) -> str:
    return r"\b" + re.escape(kw)

def _determine_category(description: str) -> str:
    desc = description.lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if " " in kw:
                if kw in desc:
                    return category
            else:
                if re.search(_word_at_start(kw), desc):
                    return category
    return "Other"


def _determine_priority(description: str, category: str) -> str:
    desc = description.lower()
    for kw in URGENT_KEYWORDS:
        if re.search(_word_at_start(kw), desc):
            return "Urgent"
    if category == "Noise":
        return "Low"
    return "Standard"


def _generate_reason(description: str) -> str:
    match = re.match(r"^[^.]*\.", description)
    if match and len(match.group()) <= 150:
        return match.group().strip()
    return description[:120].strip() + "..."


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "")
    category = _determine_category(description)
    priority = _determine_priority(description, category)
    reason = _generate_reason(description)
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows_processed = 0
    rows_failed = 0
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                    rows_processed += 1
                except Exception:
                    writer.writerow({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Could not classify this complaint.",
                        "flag": "NEEDS_REVIEW",
                    })
                    rows_failed += 1

    print(f"Done. {rows_processed} processed, {rows_failed} failed. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
