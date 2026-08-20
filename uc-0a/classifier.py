"""
UC-0A — Complaint Classifier
RICE-enforced classifier for citizen complaints.
"""
import argparse
import csv
import re
from typing import Dict, List, Tuple

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

SEVERITY_PATTERNS = {
    "injury": r"\binjur(y|ed|ies)\b",
    "child": r"\bchild(ren)?\b",
    "school": r"\bschools?\b",
    "hospital": r"\bhospital(s|ised|ized)?\b",
    "ambulance": r"\bambulances?\b",
    "fire": r"\bfires?\b",
    "hazard": r"\bhazards?|hazardous\b",
    "fell": r"\bfell\b",
    "collapse": r"\bcollapse[sd]?\b",
}

CATEGORY_PATTERNS = {
    "Pothole": [
        r"\bpotholes?\b",
        r"\bcrater\b",
        r"\bmanhole\b",
    ],
    "Drain Blockage": [
        r"\bdrain(s)?\b.*?\bblock(ed|age)?\b",
        r"\bblock(ed|age)?\b.*?\bdrain(s)?\b",
        r"\bgutter\b",
        r"\bstormwater drain\b",
        r"\bmain drain\b",
    ],
    "Flooding": [
        r"\bflood(ed|s|ing)?\b",
        r"\bwaterlogg(ed|ing)\b",
        r"\bunderpass flooded\b",
        r"\bstanding in water\b",
        r"\brainwater\b",
    ],
    "Streetlight": [
        r"\bstreetlights?\b",
        r"\bstreet light\b",
        r"\blamp post\b",
        r"\blights out\b",
        r"\bflickering\b",
        r"\bdarkness\b",
        r"\bunlit\b",
        r"\bsubstation tripped\b",
    ],
    "Waste": [
        r"\bgarbage\b",
        r"\bwaste\b",
        r"\bdead animal\b",
        r"\bdumped\b",
        r"\bdumping\b",
        r"\brubbish\b",
        r"\btrash\b",
        r"\boverflowing\b",
        r"\bsmell\b",
    ],
    "Noise": [
        r"\bmusic\b",
        r"\bloud\b",
        r"\bnoise\b",
        r"\bamplifiers?\b",
        r"\bdrilling\b",
        r"\bwedding band\b",
    ],
    "Heat Hazard": [
        r"\bheat\b",
        r"\bheatwave\b",
        r"\bmelting\b",
        r"\b\d+°c\b",
        r"\bburns on contact\b",
        r"\btemperature[s]?\b",
        r"\bfull sun\b",
    ],
    "Heritage Damage": [
        r"\bheritage\b",
        r"\bhistoric\b",
        r"\bancient\b",
        r"\bmuseum\b",
    ],
    "Road Damage": [
        r"\broad surface\b",
        r"\bcracked\b",
        r"\bsinking\b",
        r"\bbroken road\b",
        r"\bfootpath\b",
        r"\broad collapsed\b",
        r"\bbuckled\b",
        r"\bpaving\b",
        r"\bsubsidence\b",
        r"\bsubsided\b",
        r"\btarmac\b",
        r"\bcobblestones\b",
    ],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to strict RICE rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty complaint description text.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # 1. Detect severity keywords
    matched_severity = []
    for sev_key, pat in SEVERITY_PATTERNS.items():
        if re.search(pat, desc_lower):
            matched_severity.append(sev_key)

    priority = "Urgent" if matched_severity else "Standard"

    # 2. Detect matching categories
    category_matches: List[Tuple[str, str]] = []
    for cat, patterns in CATEGORY_PATTERNS.items():
        for pat in patterns:
            match = re.search(pat, desc_lower)
            if match:
                category_matches.append((cat, match.group(0)))
                break

    unique_matched_cats = list(dict.fromkeys([m[0] for m in category_matches]))

    category = "Other"
    flag = ""
    evidence_words = []

    if len(unique_matched_cats) == 1:
        category = unique_matched_cats[0]
        evidence_words = [m[1] for m in category_matches if m[0] == category]
        flag = ""
    elif len(unique_matched_cats) > 1:
        category = unique_matched_cats[0]
        evidence_words = [m[1] for m in category_matches]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        evidence_words = [description[:30]]
        flag = "NEEDS_REVIEW"

    # Enforce allowed category whitelist strictly
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Construct clean single-sentence justification
    if category != "Other":
        cite_str = f"'{evidence_words[0]}'" if evidence_words else f"'{description[:30]}...'"
        if priority == "Urgent":
            sev_str = ", ".join(f"'{s}'" for s in matched_severity)
            reason = f"Classified as {category} with Urgent priority citing description text {cite_str} and severity trigger {sev_str}."
        else:
            reason = f"Classified as {category} with Standard priority citing description text {cite_str}."
    else:
        if priority == "Urgent":
            sev_str = ", ".join(f"'{s}'" for s in matched_severity)
            reason = f"Category ambiguous from description; assigned Urgent priority due to severity trigger {sev_str}."
        else:
            reason = "Category ambiguous or unrecognized from description text; flagged for manual review."

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
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                complaint_id = row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN"
                results.append({
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Execution error during processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                })

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
