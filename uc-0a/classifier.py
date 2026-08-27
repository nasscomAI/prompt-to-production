"""
UC-0A — Complaint Classifier
Starter file. Build this using your RICE → agents.md → skills.md → CRAFT workflow.
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

LOW_PRIORITY_KEYWORDS = [
    "smell",
    "odor",
    "smelly",
    "minor",
    "inconvenience",
    "past midnight",
    "after midnight",
    "late night",
    "low impact",
]

CATEGORY_PATTERNS = {
    "Pothole": [
        r"\bpothole(s)?\b",
        r"\btyre damage\b",
        r"\bwheel.*damage\b",
        r"\broad.*hole\b",
    ],
    "Flooding": [
        r"\bflood(ed|ing)?\b",
        r"\bwaterlogged\b",
        r"\bstanding water\b",
        r"\binundat(ed|ion)?\b",
        r"\bflood.*\b",
        r"\bunderpass flooded\b",
        r"\bbridge.*flood(s)?\b",
    ],
    "Streetlight": [
        r"\bstreetlight(s)?\b",
        r"\blight(s)? (out|off|flicker(ing)?|sparking?)\b",
        r"\bdark at night\b",
        r"\bflicker(ing)?\b",
        r"\bsparking\b",
    ],
    "Waste": [
        r"\bgarbage\b",
        r"\btrash\b",
        r"\brefuse\b",
        r"\bdump(ed|ing)?\b",
        r"\boverflowing garbage\b",
        r"\bdead animal\b",
        r"\bsmell(ing)?\b",
        r"\bwaste\b",
    ],
    "Noise": [
        r"\bmusic\b",
        r"\bnoise\b",
        r"\bloud\b",
        r"\bnight(s)?\b.*\bmusic\b",
        r"\bmidnight\b",
    ],
    "Road Damage": [
        r"\bcrack(ed|s)?\b",
        r"\bsink(ing)?\b",
        r"\bbroken\b",
        r"\bupturn(ed|ing)?\b",
        r"\broad surface\b",
        r"\broad.*damage\b",
        r"\bfootpath tiles\b",
        r"\bbridge approach\b",
        r"\broad surface cracked\b",
    ],
    "Heritage Damage": [
        r"\bheritage\b",
        r"\bhistoric\b",
        r"\bheritage street\b",
    ],
    "Heat Hazard": [
        r"\bheat( hazard)?\b",
        r"\bscorch(ing)?\b",
        r"\bheatwave\b",
        r"\btemperature\b",
    ],
    "Drain Blockage": [
        r"\bdrain(s)? (blocked|blockage|blocked)\b",
        r"\bblocked drain\b",
        r"\bdrain.*blocked\b",
        r"\bsewer\b",
    ],
}

CATEGORY_PRIORITY = [
    "Heritage Damage",
    "Flooding",
    "Drain Blockage",
    "Pothole",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heat Hazard",
    "Other",
]

COMPLAINT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

COMPILED_CATEGORY_PATTERNS = {
    category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for category, patterns in CATEGORY_PATTERNS.items()
}

SEVERITY_PATTERN = re.compile(r"\b(" + r"|".join(re.escape(word) for word in SEVERITY_KEYWORDS) + r")\b", re.IGNORECASE)
LOW_PRIORITY_PATTERN = re.compile(r"\b(" + r"|".join(re.escape(word) for word in LOW_PRIORITY_KEYWORDS) + r")\b", re.IGNORECASE)


def _safe_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _find_category_matches(text: str) -> Tuple[str, List[str], bool]:
    scores: Dict[str, int] = {}
    evidences: Dict[str, List[str]] = {}
    for category, patterns in COMPILED_CATEGORY_PATTERNS.items():
        matches: List[str] = []
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                matches.append(match.group(0))
        if matches:
            scores[category] = len(matches)
            evidences[category] = matches

    if not scores:
        return "Other", [], True

    top_score = max(scores.values())
    top_categories = [category for category, score in scores.items() if score == top_score]
    chosen = None
    if len(top_categories) == 1:
        chosen = top_categories[0]
    else:
        for category in CATEGORY_PRIORITY:
            if category in top_categories:
                chosen = category
                break

    ambiguous = len(top_categories) > 1
    chosen_evidence = evidences.get(chosen, []) if chosen else []
    return chosen or "Other", chosen_evidence, ambiguous


def _detect_priority(text: str) -> Tuple[str, str]:
    if SEVERITY_PATTERN.search(text):
        match = SEVERITY_PATTERN.search(text)
        return "Urgent", match.group(0) if match else "severity keyword"
    if LOW_PRIORITY_PATTERN.search(text):
        match = LOW_PRIORITY_PATTERN.search(text)
        return "Low", match.group(0) # pyright: ignore[reportOptionalMemberAccess]
    return "Standard", ""


def _build_reason(category: str, priority: str, description: str, evidence: List[str], priority_word: str) -> str:
    evidence_text = evidence[0] if evidence else "description wording"
    if not description:
        return "No description provided to classify this complaint."

    if category == "Other":
        return f"Could not map the complaint to a known category; description includes {evidence_text!r}."

    if priority == "Urgent":
        return (
            f"Marked Urgent because the description mentions {priority_word!r}; "
            f"category is {category} based on {evidence_text!r}."
        )

    return f"Classified as {category} based on {evidence_text!r} from the description."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = _safe_text(row.get("complaint_id"))
    description = _safe_text(row.get("description"))
    location = _safe_text(row.get("location"))
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing complaint description; cannot determine category reliably.",
            "flag": "NEEDS_REVIEW",
        }

    search_text = " ".join([description, location]).strip()
    category, evidence, ambiguous = _find_category_matches(search_text)
    priority, priority_word = _detect_priority(search_text)
    flag = "NEEDS_REVIEW" if ambiguous or category == "Other" else ""
    reason = _build_reason(category, priority, description, evidence, priority_word)

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
    with open(input_path, newline="", encoding="utf-8") as infile, open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=COMPLAINT_FIELDS)
        writer.writeheader()

        for row_number, row in enumerate(reader, start=1):
            if not any(_safe_text(value) for value in row.values()):
                continue
            try:
                classified = classify_complaint(row)
            except Exception as exc:
                complaint_id = _safe_text(row.get("complaint_id"))
                classified = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Failed to classify row {row_number}: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(classified)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
