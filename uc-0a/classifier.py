"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import logging
import re

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = [
    ("Pothole",        [r"pothole"]),
    ("Drain Blockage", [r"drain\s+\w*\s*blocked", r"drain blockage", r"blocked drain", r"stormwater drain"]),
    ("Flooding",       [r"flood", r"waterlogging", r"knee.?deep"]),
    ("Streetlight",    [r"streetlight", r"lights?\s+out", r"flickering", r"sparking", r"unlit", r"darkness"]),
    ("Waste",          [r"garbage", r"overflowing\s+bin", r"bins?\s+overflow", r"dead animal", r"bulk waste", r"dumped on", r"waste\s+not\s+cleared", r"waste\s+overflow"]),
    ("Noise",          [r"noise", r"music", r"loud"]),
    ("Road Damage",    [r"road\s+surface", r"cracked", r"sinking", r"footpath", r"pavement", r"road\s+damage", r"collaps", r"crater"]),
    ("Heritage Damage",[r"heritage"]),
    ("Heat Hazard",    [r"heat"]),
]


def _match_categories(desc_lower: str) -> list:
    matched = []
    for cat, patterns in CATEGORY_RULES:
        if any(re.search(p, desc_lower) for p in patterns):
            matched.append(cat)
    return matched


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    complaint_id = (row.get("complaint_id") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description — cannot classify",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()
    matched = _match_categories(desc_lower)

    if len(matched) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched) == 1:
        category = matched[0]
        flag = ""
    else:
        if "Heritage Damage" in matched and len(matched) > 1:
            category = [c for c in matched if c != "Heritage Damage"][0]
            flag = ""
        elif "Flooding" in matched and "Drain Blockage" in matched:
            category = "Flooding"
            flag = ""
        else:
            category = matched[0]
            flag = ""

    priority = "Urgent" if any(kw in desc_lower for kw in SEVERITY_KEYWORDS) else "Standard"

    words = description.lower().split()
    cited = " ".join(words[:12])
    if len(words) > 12:
        cited += "..."
    reason = f"Complaint about {category.lower()}: \"{cited}\""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            if not row.get("complaint_id", "").strip():
                logging.warning("Row %d skipped: missing complaint_id", i)
                continue
            if not row.get("description", "").strip():
                logging.warning("Row %d skipped: missing description", i)
                continue
            rows.append(row)

    results = [classify_complaint(r) for r in rows]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
