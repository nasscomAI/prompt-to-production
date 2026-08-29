"""UC-0A — Complaint Classifier"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = frozenset([
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
])
ALLOWED_PRIORITIES = frozenset(["Urgent", "Standard", "Low"])
SEVERITY_KEYWORDS = frozenset([
    "injury", "child", "school", "hospital", "ambulance", "fire",
    "hazard", "fell", "collapse",
])

GENERIC_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "rainwater", "waterlogging", "water accumulation", "knee-deep"],
    "Streetlight": ["streetlight"],
    "Waste": ["garbage", "waste", "rubbish", "dumped", "not cleared", "not removed", "overflow"],
    "Noise": ["music", "noise", "loud", "drilling"],
    "Road Damage": ["footpath", "cracked", "sinking", "broken", "tiles", "manhole", "collapsed", "crater"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "temperature"],
    "Drain Blockage": ["drain", "blocked", "drainage"],
}


def _classify_category(description: str) -> str:
    desc_lower = description.lower()

    matched = set()
    for cat, keywords in GENERIC_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched.add(cat)
                break

    if len(matched) == 0:
        return "Other"
    if len(matched) == 1:
        return next(iter(matched))

    matched_list = sorted(matched)

    if "Heritage Damage" in matched and "Waste" in matched:
        matched.discard("Waste")

    if {"Drain Blockage", "Flooding"}.issubset(matched):
        flood_pos = min(desc_lower.find(kw) for kw in ["flood", "flooded"] if kw in desc_lower)
        drain_pos = min(desc_lower.find(kw) for kw in ["drain", "blocked"] if kw in desc_lower)
        if flood_pos < drain_pos:
            matched.discard("Drain Blockage")
        else:
            matched.discard("Flooding")

    if len(matched) == 1:
        return next(iter(matched))

    return "Other"


def _has_severity(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in SEVERITY_KEYWORDS)


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "") or ""

    category = _classify_category(description)
    priority = "Urgent" if _has_severity(description) else "Standard"

    if description.strip():
        sentences = [s.strip() for s in re.split(r"[.!?]+", description) if s.strip()]
        reason_sentence = sentences[0] + "." if sentences else description.strip()
        if not reason_sentence.endswith("."):
            reason_sentence += "."
    else:
        reason_sentence = "No description provided."

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason_sentence,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": "Could not classify row.",
                "flag": "NEEDS_REVIEW",
            })

    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")