"""
UC-0A — Complaint Classifier
RICE-compliant implementation guided by agents.md and skills.md.
"""
import argparse
import csv
import re

# Severity keywords specified in uc-0a/README.md and agents.md
SEVERITY_KEYWORDS = {
    'injury', 'injured', 'injuries',
    'child', 'children',
    'school',
    'hospital', 'hospitalised', 'hospitalized',
    'ambulance',
    'fire',
    'hazard',
    'fell',
    'collapse', 'collapsed'
}

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
    "Other"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row into category, priority, reason, and flag fields.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "") or "").strip() or "UNKNOWN"
    raw_description = str(row.get("description", "") or "").strip()

    # Null or empty description handling
    if not raw_description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty complaint description.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = raw_description.lower()

    # 1. Determine Priority based on Severity Keywords
    matched_severity = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            matched_severity.append(kw)

    priority = "Urgent" if matched_severity else "Standard"

    # 2. Category Scoring & Matching
    scores = {cat: 0 for cat in ALLOWED_CATEGORIES if cat != "Other"}

    category_patterns = {
        "Pothole": [r'\bpotholes?\b', r'\bcrater\b', r'\bpit\b'],
        "Flooding": [r'\bflooded\b', r'\bflooding\b', r'\bfloods\b', r'\bwaterlogg?(ed|ing)?\b', r'\binundated\b', r'\bstanding water\b', r'\brainwater\b'],
        "Drain Blockage": [r'\bdrains?\b', r'\bdrainage\b', r'\bgutters?\b', r'\bsewer\b', r'\bclogged\b', r'\bclogging\b', r'\bblocked drain\b'],
        "Streetlight": [r'\bstreetlights?\b', r'\bstreet light\b', r'\blights out\b', r'\bunlit\b', r'\bdarkness\b', r'\bdark at night\b', r'\blamp post\b', r'\bsubstation tripped\b', r'\bflickering\b'],
        "Waste": [r'\bgarbages?\b', r'\btrash\b', r'\bwaste\b', r'\bdumped\b', r'\bdebris\b', r'\bdead animal\b', r'\brefuse\b', r'\bbins?\b', r'\boverflowing\b'],
        "Noise": [r'\bmusic\b', r'\bloudspeakers?\b', r'\bnoise\b', r'\bdrilling\b', r'\bamplifiers?\b', r'\bidling\b'],
        "Heat Hazard": [r'\bheat\b', r'\bheatwave\b', r'\btemperatures?\b', r'\b\d+°c\b', r'\bmelting\b', r'\bsunstroke\b', r'\bfull sun\b', r'\bburns on contact\b'],
        "Heritage Damage": [r'\bheritage\b', r'\bhistoric\b', r'\bancient\b', r'\bmonument\b', r'\btagore museum\b', r'\bmarble palace\b', r'\bbow barracks\b', r'\bstep well\b'],
        "Road Damage": [r'\broad surface\b', r'\btarmac\b', r'\bcracked\b', r'\bsinking\b', r'\bmanhole\b', r'\bfootpaths?\b', r'\bpaving\b', r'\btiles broken\b', r'\broad collapsed?\b', r'\broad damage\b', r'\bsubsidence\b', r'\bcobblestones\b', r'\bbuckled\b']
    }

    for cat, patterns in category_patterns.items():
        for pat in patterns:
            matches = re.findall(pat, desc_lower)
            if matches:
                scores[cat] += len(matches)

    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_cat, top_score = sorted_cats[0]
    second_cat, second_score = sorted_cats[1]

    flag = ""
    category = top_cat

    if top_score == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif second_score > 0 and second_score == top_score:
        flag = "NEEDS_REVIEW"
    elif "heritage" in desc_lower and top_cat != "Heritage Damage":
        flag = "NEEDS_REVIEW"

    # 3. Construct Reason citing specific words from description
    excerpt = raw_description if len(raw_description) <= 65 else raw_description[:62] + "..."
    reason = f"Classified as {category} ({priority}) citing description: '{excerpt}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    try:
        with open(input_path, mode="r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=1):
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as row_err:
                    cid = row.get("complaint_id", f"ROW-{row_idx}") if isinstance(row, dict) else f"ROW-{row_idx}"
                    results.append({
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {str(row_err)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as file_err:
        print(f"Error reading input CSV {input_path}: {file_err}")
        return

    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
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

