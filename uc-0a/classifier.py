"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
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
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "floods", "rainwater", "waterlogged", "underpass"],
    "Streetlight": ["streetlight", "streetlights", "lamp post", "lights out", "unlit", "darkness"],
    "Waste": ["garbage", "waste", "bins", "dead animal", "dumped", "not cleared"],
    "Noise": ["music", "amplifiers", "drilling", "band", "audible", "engines on", "playing"],
    "Road Damage": [
        "road surface",
        "cracked",
        "sinking",
        "subsided",
        "buckled",
        "collapsed",
        "crater",
        "footpath",
        "paving",
        "tiles broken",
        "manhole",
    ],
    "Heritage Damage": ["heritage", "historic", "museum", "cobblestones", "defaced", "ancient"],
    "Heat Hazard": [
        "heat",
        "heatwave",
        "44°c",
        "45°c",
        "52°c",
        "temperature",
        "melting",
        "dangerous temperatures",
        "full sun",
        "burns",
    ],
    "Drain Blockage": ["drain", "blocked", "blockage", "stormwater", "debris", "mosquito"],
}

CATEGORY_PRECEDENCE = [
    "Pothole",
    "Drain Blockage",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Heritage Damage",
    "Heat Hazard",
    "Road Damage",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _description_from(row: dict) -> str:
    value = row.get("description") or row.get("complaint") or row.get("details") or ""
    return str(value).strip()


def _matched_terms(description: str, terms: list[str]) -> list[str]:
    normalized = _normalize(description)
    return [term for term in terms if term in normalized]


def _select_category(description: str) -> tuple[str, bool, str]:
    matches = {
        category: _matched_terms(description, keywords)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    matches = {category: terms for category, terms in matches.items() if terms}

    if not matches:
        return "Other", True, ""

    highest_score = max(len(terms) for terms in matches.values())
    top_categories = [
        category for category, terms in matches.items() if len(terms) == highest_score
    ]

    if len(top_categories) > 1:
        for category in CATEGORY_PRECEDENCE:
            if category in top_categories:
                return category, True, matches[category][0]

    category = top_categories[0]
    return category, False, matches[category][0]


def _priority_for(description: str) -> tuple[str, str]:
    normalized = _normalize(description)
    for keyword in SEVERITY_KEYWORDS:
        if keyword in normalized:
            return "Urgent", keyword
    return "Standard", ""


def _reason_for(category: str, priority: str, description: str, evidence: str, severity: str) -> str:
    if not description:
        return "No complaint description was provided, so the row needs review."

    quoted_evidence = evidence or description.split(".")[0][:80]
    if severity:
        return f"Classified as {category} because the description mentions '{quoted_evidence}' and urgent keyword '{severity}'."
    return f"Classified as {category} because the description mentions '{quoted_evidence}'."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""

    if not isinstance(row, dict):
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No complaint description was provided, so the row needs review.",
            "flag": "NEEDS_REVIEW",
        }

    description = _description_from(row)
    if len(description) < 8:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No complaint description was provided, so the row needs review.",
            "flag": "NEEDS_REVIEW",
        }

    category, ambiguous, evidence = _select_category(description)
    priority, severity = _priority_for(description)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": _reason_for(category, priority, description, evidence, severity),
        "flag": "NEEDS_REVIEW" if ambiguous else "",
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as input_file, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            if not row or not any(str(value).strip() for value in row.values() if value):
                continue

            try:
                classified = classify_complaint(row)
            except Exception as exc:
                classified = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row could not be classified from the provided description: {exc}.",
                    "flag": "NEEDS_REVIEW",
                }

            writer.writerow({field: classified.get(field, "") for field in fieldnames})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
