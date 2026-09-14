"""
UC-0A — Complaint Classifier
Deterministic, stdlib-only rule engine. See agents.md / skills.md for the
enforcement rules this file implements.
"""
import argparse
import csv
import re

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "floods", "knee-deep", "water-logged", "waterlogged"],
    "Streetlight": ["streetlight", "streetlights", "street light", "lamp", "flickering", "sparking"],
    "Waste": ["garbage", "waste", "bin", "bins", "dumped", "dead animal", "rubbish"],
    "Noise": ["noise", "music", "loud", "amplifier", "drilling"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath", "manhole", "pavement"],
    "Heritage Damage": ["heritage", "historic", "monument"],
    "Heat Hazard": ["heatwave", "heat wave", "extreme heat", "sunstroke", "temperature"],
    "Drain Blockage": ["drain blocked", "blocked drain", "drainage", "drain overflow", "sewage"],
}

SEVERITY_KEYWORDS = [
    "injury", "injured", "injuries",
    "child", "children",
    "school",
    "hospital", "hospitalised", "hospitalized",
    "ambulance",
    "fire",
    "hazard", "hazardous",
    "fell", "fall",
    "collapse", "collapsed",
]


def _find_hits(text: str, keywords: list) -> list:
    lowered = text.lower()
    hits = []
    for kw in keywords:
        if re.search(r"\b" + re.escape(kw) + r"\b", lowered):
            hits.append(kw)
    return hits


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description was empty; nothing to classify from.",
            "flag": "NEEDS_REVIEW",
        }

    matched = {cat: _find_hits(description, kws) for cat, kws in CATEGORY_KEYWORDS.items()}
    matched = {cat: hits for cat, hits in matched.items() if hits}

    severity_hits = _find_hits(description, SEVERITY_KEYWORDS)
    priority = "Urgent" if severity_hits else "Standard"

    if len(matched) == 1:
        category, hits = next(iter(matched.items()))
        flag = ""
        reason = f"Matched '{hits[0]}' → {category}."
        if priority == "Urgent":
            reason += f" Urgent: description contains severity keyword '{severity_hits[0]}'."
    elif len(matched) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No category keywords matched this description; needs human review."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        tied = ", ".join(matched.keys())
        reason = f"Ambiguous: description matches multiple categories ({tied}); needs human review."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = []
        for row in reader:
            try:
                rows.append(classify_complaint(row))
            except Exception as exc:
                rows.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row failed to classify ({exc}); flagged for review.",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
