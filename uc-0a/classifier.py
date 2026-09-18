"""UC-0A complaint classifier with deterministic rule enforcement."""
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

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "children",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
    "collapsed",
]

PRIORITY_LOW_HINTS = ["minor", "small", "low priority", "not urgent", "whenever possible"]

CATEGORY_PATTERNS = {
    "Pothole": [
        r"\bpotholes?\b",
        r"\broad\s+hole\b",
        r"\bcrater(s)?\b",
    ],
    "Flooding": [
        r"\bflood(ed|ing|s)?\b",
        r"\bwater\s*-?\s*log(g(ed|ing)?)?\b",
        r"\binundat(ed|ion)?\b",
        r"\bunderpass\s+flood(ed|s|ing)?\b",
    ],
    "Streetlight": [
        r"\bstreet\s*lights?\b",
        r"\bstreetlight(s)?\b",
        r"\blamp\s*posts?\b",
        r"\blight\s*poles?\b",
        r"\bunlit\b",
        r"\bdark(ness)?\b",
        r"\bno\s+lights?\b",
    ],
    "Waste": [
        r"\bgarbage\b",
        r"\btrash\b",
        r"\bwaste\b",
        r"\bdumping\b",
        r"\boverflow(ing)?\s+bin(s)?\b",
        r"\buncollected\b",
        r"\bdead\s+animal\b",
        r"\bcarcass\b",
    ],
    "Noise": [
        r"\bnoise\b",
        r"\bloud\b",
        r"\bblaring\b",
        r"\bhorn(s)?\b",
        r"\bmusic\b",
        r"\bband\b",
        r"\bdrilling\b",
        r"\bidling\b",
        r"\bloud\s*speaker(s)?\b",
        r"\bspeaker(s)?\b",
    ],
    "Road Damage": [
        r"\broad\s+damage\b",
        r"\bbroken\s+road\b",
        r"\bcrack(ed|ing|s)?\b",
        r"\bdamaged\s+road\b",
        r"\buneven\s+road\b",
        r"\bsinkhole\b",
        r"\broad\s+surface\b",
        r"\bsinking\b",
        r"\bsubsided\b",
        r"\bbuckled\b",
        r"\bcollapsed\b",
    ],
    "Heritage Damage": [
        r"\bheritage\b",
        r"\bmonument(s)?\b",
        r"\bhistoric(al)?\b",
        r"\bprotected\s+structure\b",
        r"\bvandal(ism|ized)?\b",
    ],
    "Heat Hazard": [
        r"\bheat\s*wave\b",
        r"\bheat\b",
        r"\bhigh\s+temperature\b",
        r"\bunbearable\b",
        r"\bdangerous\s+temperature(s)?\b",
        r"\b4[0-9]\s?°?c\b",
        r"\bno\s+shade\b",
        r"\bheat\s+stroke\b",
        r"\bsun\s+exposure\b",
    ],
    "Drain Blockage": [
        r"\bdrain(s)?\b",
        r"\bblocked\s+drain(s)?\b",
        r"\bchoked\s+drain(s)?\b",
        r"\bsewer\s+block(age)?\b",
        r"\bclogged\s+drain(s)?\b",
        r"\bstorm\s*water\s+drain(s)?\b",
        r"\bdrain\s+blocked\b",
    ],
}


def _as_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _get_complaint_id(row: dict, fallback_index: int = 0) -> str:
    for key in ("complaint_id", "id", "ticket_id", "case_id"):
        value = _as_text(row.get(key, ""))
        if value:
            return value
    return f"row_{fallback_index}"


def _get_description_text(row: dict) -> str:
    preferred_keys = ["description", "complaint", "complaint_text", "details", "issue", "title", "type"]
    parts = []
    for key in preferred_keys:
        value = _as_text(row.get(key, ""))
        if value:
            parts.append(value)
    if parts:
        return " ".join(parts)

    for key, value in row.items():
        if key in {"complaint_id", "id", "ticket_id", "case_id", "category", "priority", "priority_flag", "reason", "flag"}:
            continue
        text = _as_text(value)
        if text:
            parts.append(text)
    return " ".join(parts)


def _contains_keyword(text: str, keyword: str) -> bool:
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def _collect_keyword_matches(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if _contains_keyword(text, term)]


def _collect_pattern_matches(text: str, patterns: list[str]) -> list[str]:
    matches: list[str] = []
    for pattern in patterns:
        found = re.search(pattern, text, flags=re.IGNORECASE)
        if found:
            matches.append(found.group(0).strip())
    return matches


def _select_category(matched_categories: dict[str, list[str]]) -> tuple[str, bool, list[str]]:
    if not matched_categories:
        return "Other", True, []

    if len(matched_categories) == 1:
        only_category = next(iter(matched_categories))
        return only_category, False, matched_categories[only_category]

    scored = sorted(
        ((category, len(set(matches)), matches) for category, matches in matched_categories.items()),
        key=lambda item: item[1],
        reverse=True,
    )

    top_category, top_score, top_matches = scored[0]
    second_score = scored[1][1]

    if top_score >= 2 and top_score > second_score:
        return top_category, False, top_matches

    evidence = []
    for _, _, matches in scored:
        evidence.extend(matches)
    return "Other", True, evidence


def _build_reason(category: str, priority: str, evidence: list[str], needs_review: bool, raw_text: str) -> str:
    if evidence:
        evidence_text = ", ".join(f"'{item}'" for item in list(dict.fromkeys(evidence))[:3])
    else:
        excerpt = raw_text[:60].strip()
        evidence_text = f"'{excerpt}'" if excerpt else "no descriptive words"

    if needs_review:
        return f"Marked as {category} with NEEDS_REVIEW because the description is ambiguous based on {evidence_text}."
    return f"Classified as {category} with {priority} priority based on words {evidence_text} in the complaint description."


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row into complaint_id, category, priority, reason, flag."""
    complaint_id = _get_complaint_id(row)
    description = _get_description_text(row)
    normalized = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Marked as Other with NEEDS_REVIEW because no descriptive words were provided.",
            "flag": "NEEDS_REVIEW",
        }

    matched_categories: dict[str, list[str]] = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        matches = _collect_pattern_matches(normalized, patterns)
        if matches:
            matched_categories[category] = matches

    severity_matches = _collect_keyword_matches(normalized, SEVERITY_KEYWORDS)
    if severity_matches:
        priority = "Urgent"
    elif _collect_keyword_matches(normalized, PRIORITY_LOW_HINTS):
        priority = "Low"
    else:
        priority = "Standard"

    category, needs_review, category_evidence = _select_category(matched_categories)
    flag = "NEEDS_REVIEW" if needs_review else ""
    evidence = category_evidence + severity_matches
    reason = _build_reason(category, priority, evidence, needs_review, description)

    return {
        "complaint_id": complaint_id,
        "category": category if category in ALLOWED_CATEGORIES else "Other",
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row safely, and write output CSV."""
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    rows_out = []

    with open(input_path, "r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        for index, row in enumerate(reader, start=1):
            try:
                classified = classify_complaint(row or {})
                if not classified.get("complaint_id"):
                    classified["complaint_id"] = _get_complaint_id(row or {}, index)
                rows_out.append(classified)
            except Exception as error:
                rows_out.append(
                    {
                        "complaint_id": _get_complaint_id(row or {}, index),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Marked as Other with NEEDS_REVIEW because row processing failed: {error}.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
