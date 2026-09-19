"""
UC-0A — Complaint Classifier
Rule-based classifier that follows the enforcement rules in agents.md / skills.md.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords from README / agents.md (prefix-matched so "children", "injured" count).
SEVERITY_RE = re.compile(
    r"\b(injur\w*|child\w*|school\w*|hospital\w*|ambulance\w*|fire|fires|hazard\w*|fell|collapse\w*)\b",
    re.IGNORECASE,
)

# Keyword evidence per category. A category is only assigned when EXACTLY ONE
# category has evidence; zero or several -> Other + NEEDS_REVIEW (no silent precedence).
CATEGORY_PATTERNS = {
    "Pothole": r"\bpotholes?\b",
    "Flooding": r"\b(flood\w*|waterlog\w*|water[- ]logging|inundat\w*)\b",
    "Streetlight": r"\b(street[- ]?lights?|lights? (?:are |is )?out|lamp ?posts?|flickering)\b",
    "Waste": r"\b(garbage|waste|trash|litter|rubbish)\b",
    "Noise": r"\b(noise|noisy|loud|music|speakers?|amplifiers?|drilling)\b",
    "Road Damage": r"\b(road surface|cracked|sinking|footpath|broken road|damaged road|road collapsed|crater)\b",
    "Heritage Damage": r"\b(heritage|monument|historic\w*)\b",
    "Heat Hazard": r"\b(heat ?wave|heat ?stroke|extreme heat|heat|temperatures?)\b",
    "Drain Blockage": r"\b(drains?|sewer\w*|sewage|clogged|blocked)\b",
}
CATEGORY_RE = {c: re.compile(p, re.IGNORECASE) for c, p in CATEGORY_PATTERNS.items()}


def _quote(words):
    return " and ".join(f'"{w}"' for w in words)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is missing or empty, so no category can be determined.",
            "flag": "NEEDS_REVIEW",
        }

    # Priority: Urgent if any severity keyword is present.
    sev = SEVERITY_RE.search(description)
    priority = "Urgent" if sev else "Standard"

    # Category evidence.
    hits = {}
    for cat, rx in CATEGORY_RE.items():
        m = rx.search(description)
        if m:
            hits[cat] = m.group(0)

    if len(hits) == 1:
        category, word = next(iter(hits.items()))
        flag = ""
        reason = f'Classified as {category} because the description mentions {_quote([word])}'
    elif len(hits) > 1:
        category, flag = "Other", "NEEDS_REVIEW"
        parts = ", ".join(f'"{w}" ({c})' for c, w in hits.items())
        reason = f"The description mentions {parts}, so the category is ambiguous"
    else:
        category, flag = "Other", "NEEDS_REVIEW"
        reason = "The description has no words that clearly match any allowed category"

    if sev:
        reason += f' and priority is Urgent because it contains the severity word "{sev.group(0)}"'
    reason += "."

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
    Never crashes on a bad row: it is written as Other + NEEDS_REVIEW.
    """
    fields = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                results.append(classify_complaint(row))
            except Exception as exc:  # keep going, flag the row
                results.append({
                    "complaint_id": (row.get("complaint_id") or "").strip() if isinstance(row, dict) else "",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row {i} could not be processed ({type(exc).__name__}), so it needs manual review.",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")