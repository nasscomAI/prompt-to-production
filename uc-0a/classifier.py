"""
UC-0A — Complaint Classifier
Built using the RICE (agents.md) -> skills.md -> CRAFT workflow.
"""
import argparse
import csv
import re
from typing import Optional

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "waterlogging"],
    "Streetlight": ["streetlight", "street light", "street lamp", "lamp post", "lights out", "light flickering"],
    "Waste": ["garbage", "waste", "trash", "dumped", "dumping", "litter"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["road surface", "footpath", "pavement", "road damage", "sinking", "cracked"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heatwave", "heat wave", "heat stroke", "sunstroke", "extreme heat"],
    "Drain Blockage": ["drain block", "drain blocked", "clogged drain", "sewer block", "manhole"],
}

# Order matters: this is the exact list agents.md's enforcement rule requires.
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]


def _find_keyword_hits(text: str, keyword_map: dict) -> list:
    """Return (position, category, matched_text) for every keyword hit, ordered by where it appears in text."""
    hits = []
    for category, keywords in keyword_map.items():
        for kw in keywords:
            match = re.search(r"\b" + re.escape(kw) + r"\w*", text)
            if match:
                hits.append((match.start(), category, match.group(0)))
    hits.sort(key=lambda h: h[0])
    return hits


def _find_severity_hit(text: str) -> Optional[str]:
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\w*", text):
            return kw
    return None


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
            "reason": "No description provided, so category and priority cannot be determined.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    hits = _find_keyword_hits(text, CATEGORY_KEYWORDS)
    distinct_categories = list(dict.fromkeys(hit[1] for hit in hits))

    if not distinct_categories:
        category = "Other"
        category_reason = "no schema keywords matched the description"
        ambiguous = True
    else:
        category = distinct_categories[0]
        category_reason = f'"{hits[0][2]}" identifies it as {category}'
        ambiguous = len(distinct_categories) > 1

    severity_hit = _find_severity_hit(text)
    priority = "Urgent" if severity_hit else "Standard"

    if severity_hit:
        reason = f'Categorized as {category} because {category_reason}; priority is Urgent due to severity keyword "{severity_hit}".'
    else:
        reason = f"Categorized as {category} because {category_reason}; priority is {priority} as no severity keywords were found."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW" if ambiguous else "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as exc:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification failed: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
