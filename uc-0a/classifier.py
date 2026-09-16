"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re


OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

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
    "Pothole": ["pothole", "hole", "crater"],
    "Flooding": [
        "flood",
        "flooded",
        "flooding",
        "waterlogging",
        "waterlogged",
        "standing water",
        "rainwater",
    ],
    "Streetlight": ["streetlight", "street light", "lamp", "light pole", "dark street", "no light"],
    "Waste": ["garbage", "trash", "waste", "rubbish", "dump", "dumped", "litter", "overflowing bin"],
    "Noise": ["noise", "loud", "speaker", "honking", "music", "construction noise"],
    "Road Damage": [
        "road damage",
        "broken road",
        "damaged road",
        "cracked road",
        "uneven road",
        "bad road",
        "road surface",
        "asphalt",
    ],
    "Heritage Damage": ["heritage", "monument", "historic", "statue", "old building", "protected building"],
    "Heat Hazard": ["heat", "heatwave", "heat wave", "extreme heat", "hot", "dehydration"],
    "Drain Blockage": ["drain", "drainage", "blocked drain", "clogged drain", "sewer", "manhole", "gutter"],
}

DESCRIPTION_FIELDS = ["description", "complaint", "complaint_description", "details", "issue", "text"]


def _word_pattern(term: str) -> str:
    escaped = re.escape(term)
    if " " in term:
        return rf"(?<!\w){escaped}(?!\w)"
    return rf"\b{escaped}\b"


def _find_matches(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if re.search(_word_pattern(term), text, re.IGNORECASE)]


def _get_description(row: dict) -> str:
    for field in DESCRIPTION_FIELDS:
        value = row.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()

    for key, value in row.items():
        key_text = str(key).lower()
        if "description" in key_text or "complaint" in key_text:
            if value is not None and str(value).strip():
                return str(value).strip()

    return ""


def _get_complaint_id(row: dict) -> str:
    for field in ["complaint_id", "id", "ticket_id", "case_id"]:
        value = row.get(field)
        if value is not None:
            return str(value).strip()
    return ""


def _priority(description: str) -> tuple[str, list[str]]:
    severity_matches = _find_matches(description, SEVERITY_KEYWORDS)
    if severity_matches:
        return "Urgent", severity_matches
    return "Standard", []


def _category(description: str) -> tuple[str, list[str], bool]:
    scored = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = _find_matches(description, keywords)
        if matches:
            scored.append((category, matches))

    if not scored:
        return "Other", [], True

    highest_score = max(len(matches) for _, matches in scored)
    best = [(category, matches) for category, matches in scored if len(matches) == highest_score]
    if len(best) != 1:
        all_matches = []
        for _, matches in best:
            all_matches.extend(matches)
        return "Other", all_matches, True

    category, matches = best[0]
    return category, matches, False


def _quote_terms(terms: list[str]) -> str:
    unique_terms = []
    for term in terms:
        if term not in unique_terms:
            unique_terms.append(term)
    return ", ".join(f"'{term}'" for term in unique_terms[:3])


def _reason(
    category: str,
    priority: str,
    category_terms: list[str],
    severity_terms: list[str],
    needs_review: bool,
) -> str:
    if needs_review and category_terms:
        return f"Category needs review because the description contains mixed signals such as {_quote_terms(category_terms)}."
    if needs_review:
        return "Category needs review because the description is missing or does not contain a supported complaint keyword."

    reason = f"Classified as {category} because the description mentions {_quote_terms(category_terms)}"
    if priority == "Urgent":
        reason += f", and priority is Urgent because it also mentions {_quote_terms(severity_terms)}"
    return reason + "."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        row = {}

    complaint_id = _get_complaint_id(row)
    description = _get_description(row)
    priority, severity_terms = _priority(description)

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": _reason("Other", priority, [], severity_terms, True),
            "flag": "NEEDS_REVIEW",
        }

    category, category_terms, needs_review = _category(description)
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": _reason(category, priority, category_terms, severity_terms, needs_review),
        "flag": "NEEDS_REVIEW" if needs_review else "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as input_file, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": _get_complaint_id(row) if isinstance(row, dict) else "",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Category needs review because the row could not be classified: {exc}.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow({field: result.get(field, "") for field in OUTPUT_FIELDS})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
