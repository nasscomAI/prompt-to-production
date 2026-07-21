"""
UC-0A — Complaint Classifier
Implementation based on RICE agents.md and skills.md enforcement rules.
"""
import argparse
import csv
import os
import re

ALLOWED_CATEGORIES = [
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

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

CATEGORY_PATTERNS = [
    ("Heritage Damage", r"\bheritage\b"),
    ("Heat Hazard", r"\b(heat|heatwave|sunstroke|melting|temperature|temperatures|°c|sun)\b"),
    ("Drain Blockage", r"\b(drain|draining|sewer|drainage|blocked drain)\b"),
    ("Pothole", r"\b(pothole|potholes|manhole)\b"),
    ("Flooding", r"\b(flood|flooded|floods|waterlogging|rainwater|inaccessible|stranded)\b"),
    ("Streetlight", r"\b(streetlight|streetlights|light|lights|sparking|dark|darkness|substation|unlit)\b"),
    ("Waste", r"\b(garbage|waste|dumped|trash|bins|dead animal|smell|dumping|overflow)\b"),
    ("Noise", r"\b(music|noise|loudspeaker|sound|midnight|drilling|idling|band|amplifier|amplifiers)\b"),
    ("Road Damage", r"\b(road surface|cracked|sinking|footpath|tiles|road damage|collapse|collapsed|crater|cobblestones|paving|trees?)\b"),
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row into category, priority, reason, and flag.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    desc_lower = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Complaint description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    # 1. Determine Category
    matched_category = None
    matched_cat_word = None

    for cat_name, pattern in CATEGORY_PATTERNS:
        match = re.search(pattern, desc_lower)
        if match:
            matched_category = cat_name
            matched_cat_word = match.group(0)
            break

    if not matched_category:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cat_reason = "category is unmapped"
    else:
        category = matched_category
        flag = ""
        cat_reason = f"categorized as {category} citing '{matched_cat_word}'"

    # 2. Determine Priority & Severity Triggers
    found_severity_words = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if found_severity_words:
        priority = "Urgent"
        sev_reason = f"priority set to Urgent due to severity trigger(s) '{', '.join(found_severity_words)}'"
    else:
        priority = "Standard"
        sev_reason = "priority set to Standard"

    # 3. Construct Reason (Single sentence citing verbatim words)
    reason = f"Complaint {complaint_id} {cat_reason} and {sev_reason}."

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
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as e:
                classified = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Failed to classify row due to error: {str(e)}.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(classified)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
