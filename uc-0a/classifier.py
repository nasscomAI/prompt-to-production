"""
UC-0A — Complaint Classifier
Classifies citizen complaints per agents.md enforcement rules:
exact taxonomy, Urgent severity keywords, cited reason, NEEDS_REVIEW on ambiguity.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = (
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
)

URGENT_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

CATEGORY_RULES = (
    ("Pothole", ("pothole",)),
    ("Flooding", ("flood", "standing water", "water log", "submerged", "knee-deep")),
    ("Streetlight", ("streetlight", "street light", "lights out", "light out", "flicker", "spark", "unlit", "dark")),
    ("Waste", ("garbage", "bin", "waste", "dead animal", "litter", "dumped", "overflow")),
    ("Noise", ("music", "noise", "loud", "horn", "bark", "drill", "idle", "engine", "band", "amplifier")),
    ("Road Damage", ("crack", "sink", "manhole", "footpath", "tile", "buckle", "paving", "subside", "subsidence", "cobblestone", "crater", "collapse")),
    ("Heritage Damage", ("heritage", "historic")),
    ("Heat Hazard", ("heat", "heatwave", "hot", "temperature", "sun", "\u00b0c")),
    ("Drain Blockage", ("drain", "drainage", "block")),
)

_INFLECT = r"(?:es|ed|ing|s|d|ness)?\b"


def _keyword_pattern(keyword: str) -> re.Pattern:
    # Multi-word / non-alpha keywords (spaces, "°c") are distinctive enough for
    # plain substring matching; single words get word boundaries + inflections
    # so "band" does not match "abandoned" or "sun" match "Sunday".
    if any(not ch.isalnum() for ch in keyword):
        return re.compile(re.escape(keyword))
    return re.compile(r"\b" + re.escape(keyword) + _INFLECT)


CATEGORY_PATTERNS = {
    category: [_keyword_pattern(kw) for kw in keywords]
    for category, keywords in CATEGORY_RULES
}


def _trim(text: str, limit: int = 45) -> str:
    text = text.strip().rstrip(".,;")
    return text[:limit] + ("..." if len(text) > limit else "")


def _excerpt(description: str, category: str) -> str:
    clauses = [p.strip() for p in description.replace(";", ".").split(".") if p.strip()]
    if category != "Other":
        for clause in clauses:
            if any(pattern.search(clause.lower()) for pattern in CATEGORY_PATTERNS[category]):
                return _trim(clause)
    for clause in clauses:
        if len(clause) >= 10:
            return _trim(clause)
    return _trim(description)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided to classify from.",
            "flag": "NEEDS_REVIEW",
        }

    lowered = description.lower()

    # Category: highest keyword-match score wins; a close runner-up means the
    # category is genuinely ambiguous and the row gets flagged for review.
    scored = sorted(
        ((sum(1 for pattern in CATEGORY_PATTERNS[category] if pattern.search(lowered)), category)
         for category in CATEGORY_PATTERNS),
        key=lambda item: item[0],
        reverse=True,
    )
    top_score, category = scored[0]
    second_score = scored[1][0]

    flag = ""
    if top_score == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif second_score > 0 and top_score - second_score <= 1:
        flag = "NEEDS_REVIEW"

    # Priority: Urgent on severity keywords; routine noise is Low; else Standard.
    if any(kw in lowered for kw in URGENT_KEYWORDS):
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

    reason = f'Classified as {category} because the description states "{_excerpt(description, category)}".'

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
    results = []
    with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            if not any((v or "").strip() for v in row.values()):
                continue
            try:
                verdict = classify_complaint(row)
            except Exception:
                verdict = {
                    "complaint_id": str(row.get("complaint_id", "")).strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row could not be parsed.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append([
                verdict["complaint_id"],
                verdict["category"],
                verdict["priority"],
                verdict["reason"],
                verdict["flag"],
            ])

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["complaint_id", "category", "priority", "reason", "flag"])
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")