import argparse
import csv
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

SEVERITY_PATTERNS = [
    ("injury", r"\binjur(y|ies|ed)?\b"),
    ("child", r"\bchild(ren)?\b"),
    ("school", r"\bschool(s)?\b"),
    ("hospital", r"\bhospital(s|ised|ized)?\b"),
    ("ambulance", r"\bambulance(s)?\b"),
    ("fire", r"\bfire(s)?\b"),
    ("hazard", r"\bhazard(s|ous)?\b"),
    ("fell", r"\bfell\b"),
    ("collapse", r"\bcollapse(d|s)?\b"),
]

CATEGORY_RULES = [
    ("Pothole", [
        r"\bpothole(s)?\b",
    ]),
    ("Flooding", [
        r"\bflood(ed|ing|s)?\b",
        r"\bknee-deep\b",
        r"\bwaterlogged\b",
        r"\brainwater\b",
    ]),
    ("Streetlight", [
        r"\bstreetlight(s)?\b",
        r"\bstreet light(s|ing)?\b",
        r"\blights? out\b",
        r"\blamp(s)?\b",
        r"\bunlit\b",
        r"\bdarkness\b",
    ]),
    ("Waste", [
        r"\bgarbage\b",
        r"\bwaste\b",
        r"\bbins?\b",
        r"\bdead animal\b",
        r"\bdump(ed)?\b",
        r"\bdebris\b",
    ]),
    ("Noise", [
        r"\bnoise\b",
        r"\bmusic\b",
        r"\bloudspeaker(s)?\b",
        r"\bdecibel\b",
        r"\bwedding band\b",
        r"\bdrilling\b",
        r"\bengines on\b",
        r"\bamplifier(s)?\b",
    ]),
    ("Drain Blockage", [
        r"\bdrain(s|ed)?\b",
        r"\bblockage\b",
        r"\bblocked drain\b",
        r"\bdrainage\b",
        r"\bmanhole\b",
    ]),
    ("Heritage Damage", [
        r"\bheritage\b",
        r"\bmonument(s)?\b",
        r"\bhistoric(al)?\b",
        r"\bancient\b",
    ]),
    ("Heat Hazard", [
        r"\bheat\b",
        r"\bheatwave\b",
        r"\bsunstroke\b",
        r"\btemperature(s)?\b",
        r"\bmelting\b",
        r"\b\d+°c\b",
        r"\bfull sun\b",
        r"\bburns on contact\b",
    ]),
    ("Road Damage", [
        r"\broad surface\b",
        r"\bfootpath\b",
        r"\btiles broken\b",
        r"\bsinking\b",
        r"\bcracked\b",
        r"\bpaving\b",
        r"\bbuckled\b",
        r"\bsubsid(ed|ence)\b",
        r"\bcrater\b",
        r"\bcobblestone(s)?\b",
    ]),
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to UC-0A specification.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    desc = (row.get("description") or "").strip()

    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing complaint description.",
            "flag": "NEEDS_REVIEW",
        }

    lower_desc = desc.lower()

    # Priority determination: Urgent if severity keywords present
    triggered_severity = []
    for kw_name, pattern in SEVERITY_PATTERNS:
        match = re.search(pattern, lower_desc)
        if match:
            triggered_severity.append(match.group(0))

    priority = "Urgent" if triggered_severity else "Standard"

    # Category matching
    matched_categories = []
    matched_phrases = []
    for cat, patterns in CATEGORY_RULES:
        for pat in patterns:
            match = re.search(pat, lower_desc)
            if match:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_phrases.append(match.group(0))

    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
        cite = matched_phrases[0]
    elif len(matched_categories) > 1:
        # Genuinely ambiguous complaint matching multiple categories
        category = matched_categories[0]
        cite = ", ".join(matched_phrases)
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        cite = desc[:30]
        flag = "NEEDS_REVIEW"

    # Strict taxonomy check
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # One sentence justification citing specific words from description
    if triggered_severity:
        reason = f"Classified as {category} based on '{cite}'; marked Urgent due to severity keyword '{triggered_severity[0]}'."
    else:
        reason = f"Classified as {category} because description refers to '{cite}'."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {str(e)}",
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
