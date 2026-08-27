"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

ALLOWED_CATEGORIES = {
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
}

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

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "road pit"],
    "Flooding": ["flood", "flooded", "waterlogged", "water logging", "knee-deep"],
    "Streetlight": ["streetlight", "street light", "lamp post", "dark street", "lights off", "light not working"],
    "Waste": ["garbage", "waste", "trash", "dump", "litter", "bin overflow", "overflowing bin", "stink"],
    "Noise": ["noise", "loud", "honking", "speaker", "dj", "construction noise", "blaring"],
    "Road Damage": ["road damage", "crack", "broken road", "uneven road", "caved", "road sinking"],
    "Heritage Damage": ["heritage", "monument", "statue", "historic", "fort wall", "old structure"],
    "Heat Hazard": ["heat", "heatwave", "no shade", "heat hazard", "sunstroke", "high temperature"],
    "Drain Blockage": ["drain blocked", "blocked drain", "clogged drain", "sewer choke", "manhole overflow", "drain overflow"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = (row or {}).get("complaint_id", "") or "UNKNOWN_ID"
    description_raw = (row or {}).get("description", "") or ""
    description = description_raw.strip()
    text = description.lower()

    matched_categories = []
    matched_terms = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        local_hits = [kw for kw in keywords if kw in text]
        if local_hits:
            matched_categories.append(category)
            matched_terms.extend(local_hits)

    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in text]

    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"

    priority = "Urgent" if severity_hits else "Standard"
    if not description:
        priority = "Low"
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Description is empty, so this row needs manual review."
    else:
        cited_terms = severity_hits + matched_terms
        cited_terms = list(dict.fromkeys(cited_terms))
        if cited_terms:
            reason = f"Matched words from description: {', '.join(cited_terms[:4])}."
        else:
            reason = "No clear category keywords found in description, so manual review is needed."

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
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                # Keep processing even if a malformed row fails classification.
                complaint_id = (row or {}).get("complaint_id", "") or "UNKNOWN_ID"
                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification failed due to row error: {type(exc).__name__}.",
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
