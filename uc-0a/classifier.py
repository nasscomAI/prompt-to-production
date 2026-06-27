"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

REQUIRED_KEYS = frozenset([
    "complaint_id", "date_raised", "city", "ward", "location",
    "description", "reported_by", "days_open",
])

SEVERITY_KEYWORDS = frozenset([
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
])

CATEGORY_RULES = [
    ("Pothole",        [r"pothole"]),
    ("Flooding",       [r"flood"]),
    ("Streetlight",    [r"streetlight", r"lights?\s+out", r"flickering", r"sparking", r"unlit"]),
    ("Waste",          [r"garbage", r"dead\s+animal", r"bulk\s+waste", r"\bwaste\b", r"dumped"]),
    ("Noise",          [r"music", r"noise", r"loud", r"wedding\s+(band|venue)", r"drilling", r"idling", r"amplifier"]),
    ("Heritage Damage",[r"heritage", r"historic"]),
    ("Heat Hazard",    [r"\bheat\b", r"\bhot\b", r"melting", r"temperature"]),
    ("Drain Blockage", [r"drain\b[^.]*?\bblock", r"blocked\s+drain", r"drainage", r"draining"]),
    ("Road Damage",    [r"road\s+surface", r"cracked", r"sinking", r"footpath",
                         r"manhole\s+cover", r"tiles?\s+broken", r"upturned",
                         r"subsid", r"collapsed"]),
]


def _validate_row(row: dict) -> None:
    missing = REQUIRED_KEYS - row.keys()
    if missing:
        raise ValueError(f"Missing required keys: {', '.join(sorted(missing))}")


def _find_category(desc_lower: str) -> str:
    for cat, patterns in CATEGORY_RULES:
        for p in patterns:
            if re.search(p, desc_lower):
                return cat
    return "Other"


def _get_priority(desc_lower: str) -> str:
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            return "Urgent"
    return "Standard"


def _generate_reason(desc: str) -> str:
    for s in desc.split("."):
        s = s.strip()
        if s:
            return s + "."
    return "Complaint received."


def classify_complaint(row: dict) -> dict:
    _validate_row(row)

    desc = row["description"]
    desc_lower = desc.lower()

    category = _find_category(desc_lower)
    priority = _get_priority(desc_lower)
    reason = _generate_reason(desc)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": row["complaint_id"],
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        raise ValueError("Input CSV is empty")

    out_rows = []
    failed = 0
    for row in rows:
        try:
            out_rows.append(classify_complaint(row))
        except Exception as e:
            failed += 1
            print(f"Skipping row {row.get('complaint_id', '?')}: {e}")

    if not out_rows:
        raise RuntimeError("No rows could be classified — no output written")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    if failed:
        print(f"Warning: {failed} row(s) failed classification")
    print(f"Done. {len(out_rows)} row(s) written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
