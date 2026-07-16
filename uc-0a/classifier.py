"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re


URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = [
    ("Pothole", ["pothole", "crater"]),
    ("Flooding", ["flood", "waterlog", "submerged", "knee.deepl"]),
    ("Streetlight", ["streetlight", "street.light", "lamp", "light out", "flickering", "lights out"]),
    ("Waste", ["garbage", "waste", "trash", "litter", "dumping", "dead animal", "overflowing.bin"]),
    ("Noise", ["noise", "loud", "music past midnight"]),
    ("Road Damage", ["road.surface", "cracked", "sinking", "road.damage", "broken road"]),
    ("Heritage Damage", ["heritage", "monument", "historical"]),
    ("Heat Hazard", ["heat", "temperature"]),
    ("Drain Blockage", ["drain", "blockage", "clogged", "manhole"]),
]


def _contains(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, re.IGNORECASE))


def _find_category(description: str) -> tuple:
    matches = [(cat, keywords) for cat, keywords in CATEGORY_RULES if any(_contains(description, kw) for kw in keywords)]
    if len(matches) == 1:
        return matches[0][0], ""
    if len(matches) > 1:
        return "Other", "NEEDS_REVIEW"
    return "Other", "NEEDS_REVIEW"


def _find_priority(description: str) -> str:
    if any(_contains(description, kw) for kw in URGENT_KEYWORDS):
        return "Urgent"
    return "Standard"


def _generate_reason(description: str) -> str:
    words = description.split()
    cited = [w.strip(".,;:!?") for w in words if len(w.strip(".,;:!?")) > 3][:10]
    if not cited:
        cited = words[:10]
    return "Description mentions: " + ", ".join(cited[:6])


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    cid = row.get("complaint_id", "").strip()

    if not description:
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    category, flag = _find_category(description)
    priority = _find_priority(description)
    reason = _generate_reason(description)

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        results = []
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception:
                cid = row.get("complaint_id", "UNKNOWN")
                results.append({
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Invalid row",
                    "flag": "NEEDS_REVIEW",
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
