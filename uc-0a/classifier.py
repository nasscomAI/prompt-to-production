"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from typing import Dict, List, Tuple

ALLOWED_CATEGORIES: List[str] = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

CATEGORY_RULES: List[Tuple[str, List[str]]] = [
    ("Pothole", ["pothole", "crater"]),
    ("Flooding", ["flood", "flooded", "waterlogged", "water logging", "underpass flooded"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "flickering", "sparking"]),
    ("Waste", ["garbage", "waste", "bins", "dead animal", "dumped"]),
    ("Noise", ["music", "loud", "noise", "midnight"]),
    ("Road Damage", ["road surface cracked", "sinking", "broken", "upturned", "manhole cover missing"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard", ["heat", "heatwave", "temperature"]),
    ("Drain Blockage", ["drain blocked", "drainage blockage", "blocked drain"]),
]


def _find_matches(text: str, terms: List[str]) -> List[str]:
    return [term for term in terms if term in text]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Classification logic is rule-based and deterministic.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description_raw = (row.get("description") or "").strip()
    description = description_raw.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description; unable to determine category confidently.",
            "flag": "NEEDS_REVIEW",
        }

    category_hits: Dict[str, List[str]] = {}
    for category, keywords in CATEGORY_RULES:
        hits = _find_matches(description, keywords)
        if hits:
            category_hits[category] = hits

    if len(category_hits) == 1:
        category = next(iter(category_hits.keys()))
        category_terms = category_hits[category]
        flag = ""
    else:
        category = "Other"
        category_terms = []
        flag = "NEEDS_REVIEW"

    severity_hits = [keyword for keyword in SEVERITY_KEYWORDS if keyword in description]
    priority = "Urgent" if severity_hits else "Standard"

    reason_parts = []
    if category_terms:
        reason_parts.append("category from words: " + ", ".join(sorted(set(category_terms[:3]))))
    else:
        reason_parts.append("category ambiguous or not explicit in complaint text")

    if severity_hits:
        reason_parts.append("urgent due to severity words: " + ", ".join(sorted(set(severity_hits))))
    else:
        reason_parts.append("no severity keywords found")

    reason = "; ".join(reason_parts) + "."

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
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
    
    Reads input CSV, classifies each row, and writes strict output columns.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile, open(
        output_path, "w", encoding="utf-8", newline=""
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as ex:
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing error: {str(ex)}.",
                    "flag": "NEEDS_REVIEW",
                }

            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
