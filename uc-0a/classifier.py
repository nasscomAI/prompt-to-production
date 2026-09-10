"""
UC-0A — Complaint Classifier
Implementation guided strictly by UC-0A schema, agents.md, and skills.md.
"""
import argparse
import csv
import os
import re

# Allowed categories strictly per UC-0A schema
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

# Allowed priorities strictly per UC-0A schema
ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Mandatory severity keywords that MUST trigger Urgent priority
SEVERITY_KEYWORDS_PATTERN = re.compile(
    r"\b(injur\w*|child\w*|school\w*|hospital\w*|ambulance\w*|fire\w*|hazard\w*|fell|collaps\w*)\b",
    re.IGNORECASE,
)

# Category patterns recognizing terminology present in the city test datasets
CATEGORY_PATTERNS = {
    "Pothole": re.compile(r"\bpotholes?\b", re.IGNORECASE),
    "Flooding": re.compile(
        r"\b(flood(s|ed|ing)?|waterlogg\w*|knee-deep)\b",
        re.IGNORECASE,
    ),
    "Streetlight": re.compile(
        r"\b(streetlight\w*|street\s*light\w*|street\s*lamp\w*|lamp\s*post\w*|lights?\s+out|unlit|darkness|dark\s+at\s+night|wiring\s+theft)\b",
        re.IGNORECASE,
    ),
    "Waste": re.compile(
        r"\b(garbage|waste|bins?|dumped|dead\s+animal)\b",
        re.IGNORECASE,
    ),
    "Noise": re.compile(
        r"\b(noise|music|drilling|amplifiers?|idling\s+with\s+engines)\b",
        re.IGNORECASE,
    ),
    "Road Damage": re.compile(
        r"\b(road\s+(surface|damage|cracked|subsidence|collapsed|subsided)|footpath\w*|paving|buckled|crater)\b",
        re.IGNORECASE,
    ),
    "Heritage Damage": re.compile(
        r"\b(heritage|historic|ancient|museum|defaced)\b",
        re.IGNORECASE,
    ),
    "Heat Hazard": re.compile(
        r"\b(heat|heatwave|melting|\d+°\s*C|temperature\w*|burns\s+on\s+contact|full\s+sun)\b",
        re.IGNORECASE,
    ),
    "Drain Blockage": re.compile(
        r"\b(drain(s|ed|ing|age)?|stormwater|manhole\w*)\b",
        re.IGNORECASE,
    ),
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to the UC-0A schema.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    # Handle missing or blank description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Complaint record has an empty description field.",
            "flag": "NEEDS_REVIEW",
        }

    # 1. Match categories based on explicit schema patterns
    matched_categories = []
    for cat, pattern in CATEGORY_PATTERNS.items():
        if pattern.search(description):
            matched_categories.append(cat)

    # Ambiguity check: exactly one match is unambiguous; 0 or >1 matches require Other + NEEDS_REVIEW
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Priority check: severity keywords trigger Urgent; all non-severity cases use Standard
    severity_match = SEVERITY_KEYWORDS_PATTERN.search(description)
    if severity_match:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Split description into clean sentences for precise citation targeting
    sentences = [s.strip().rstrip(". ") for s in description.split(".") if s.strip()]

    # 3. Construct a one-sentence reason citing the exact supporting phrase
    if flag == "NEEDS_REVIEW":
        if len(matched_categories) > 1:
            cats = " and ".join(matched_categories)
            ambig_phrases = [
                s for s in sentences
                if any(CATEGORY_PATTERNS[c].search(s) for c in matched_categories)
            ]
            cited_text = " and ".join(f"'{p}'" for p in ambig_phrases) if ambig_phrases else f"'{sentences[0]}'"
            reason = (
                f"Assigned to Other with flag NEEDS_REVIEW because the description ambiguously references "
                f"{cats} citing {cited_text}."
            )
        else:
            first_sent = sentences[0] if sentences else description
            reason = (
                f"Assigned to Other with flag NEEDS_REVIEW because the category cannot be determined "
                f"from description citing '{first_sent}'."
            )
    else:
        if severity_match:
            sev_word = severity_match.group(0)
            # Find the specific sentence containing the severity keyword
            severity_sentence = next(
                (s for s in sentences if SEVERITY_KEYWORDS_PATTERN.search(s)),
                sentences[0] if sentences else description
            )
            reason = (
                f"Classified as {category} with Urgent priority due to severity keyword '{sev_word}' "
                f"in '{severity_sentence}'."
            )
        else:
            # Find the specific sentence supporting the category classification
            cat_pattern = CATEGORY_PATTERNS[category]
            category_sentence = next(
                (s for s in sentences if cat_pattern.search(s)),
                sentences[0] if sentences else description
            )
            reason = (
                f"Classified as {category} with Standard priority based on cited '{category_sentence}'."
            )

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
    Does not crash on bad rows, flags nulls, and produces output even if individual rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile)
        for row_idx, row in enumerate(reader, start=1):
            try:
                if not row or not any(row.values()):
                    results.append({
                        "complaint_id": f"ROW-{row_idx}",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row {row_idx} is blank.",
                        "flag": "NEEDS_REVIEW",
                    })
                    continue

                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                cid = row.get("complaint_id", f"ROW-{row_idx}") if isinstance(row, dict) else f"ROW-{row_idx}"
                results.append({
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing error on row {row_idx} citing '{str(e)[:30]}'.",
                    "flag": "NEEDS_REVIEW",
                })

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
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
