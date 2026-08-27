"""
UC-0A — Complaint Classifier
Implements agents.md enforcement rules and skills.md classify_complaint / batch_classify.
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

# Longer phrases first so specific signals beat generic ones (e.g. "drain blocked" vs "flood").
CATEGORY_PATTERNS: list[tuple[str, str]] = [
    ("Drain Blockage", r"\bdrain\b[^.]{0,40}\bblocked\b"),
    ("Drain Blockage", r"\bblocked\b[^.]{0,40}\bdrain\b"),
    ("Drain Blockage", r"\bdrain\s+blockage\b"),
    ("Heritage Damage", r"\bheritage\b"),
    ("Heritage Damage", r"\bhistoric\b"),
    ("Heat Hazard", r"\bheat\s+hazard\b"),
    ("Heat Hazard", r"\bextreme\s+heat\b"),
    ("Heat Hazard", r"\bheatwave\b"),
    ("Heat Hazard", r"\b\d+°C\b"),
    ("Heat Hazard", r"\btemperatures?\b"),
    ("Heat Hazard", r"\bmelting\b"),
    ("Heat Hazard", r"\bburns?\b"),
    ("Heat Hazard", r"\bheat\b"),
    ("Pothole", r"\bpotholes?\b"),
    ("Flooding", r"\bflooded\b"),
    ("Flooding", r"\bflooding\b"),
    ("Flooding", r"\bfloods?\b"),
    ("Flooding", r"\bknee-deep\b"),
    ("Flooding", r"\bstanding\s+in\s+water\b"),
    ("Flooding", r"\brainwater\b"),
    ("Flooding", r"\bdraining\b"),
    ("Streetlight", r"\bstreetlights?\b"),
    ("Streetlight", r"\blights\s+out\b"),
    ("Streetlight", r"\bdark\s+at\s+night\b"),
    ("Streetlight", r"\bunlit\b"),
    ("Streetlight", r"\bdarkness\b"),
    ("Waste", r"\bgarbage\b"),
    ("Waste", r"\bdead\s+animal\b"),
    ("Waste", r"\boverflowing\b"),
    ("Waste", r"\bbulk\s+waste\b"),
    ("Waste", r"\bdumped\b"),
    ("Waste", r"\bwaste\b"),
    ("Noise", r"\bmusic\b"),
    ("Noise", r"\bnoise\b"),
    ("Noise", r"\bdrilling\b"),
    ("Noise", r"\bengines?\b"),
    ("Noise", r"\bidling\b"),
    ("Noise", r"\bplaying\b"),
    ("Noise", r"\bband\b"),
    ("Noise", r"\bamplifiers?\b"),
    ("Road Damage", r"\broad\s+surface\b"),
    ("Road Damage", r"\bmanhole\b"),
    ("Road Damage", r"\bfootpath\b"),
    ("Road Damage", r"\btiles\s+broken\b"),
    ("Road Damage", r"\bcracked\b"),
    ("Road Damage", r"\bsinking\b"),
    ("Road Damage", r"\bupturned\b"),
    ("Road Damage", r"\bcollapsed\b"),
    ("Road Damage", r"\bsubsid"),
    ("Road Damage", r"\bbuckled\b"),
    ("Road Damage", r"\bbroken\b"),
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _description_text(row: dict) -> str:
    value = row.get("description")
    if value is None:
        return ""
    return str(value).strip()


def _find_severity_matches(description: str) -> list[str]:
    lower = description.lower()
    return [kw for kw in SEVERITY_KEYWORDS if kw in lower]


def _score_categories(description: str) -> dict[str, list[str]]:
    scores: dict[str, list[str]] = {}
    for category, pattern in CATEGORY_PATTERNS:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            scores.setdefault(category, []).append(match.group(0))
    return scores


def _pick_category(scores: dict[str, list[str]]) -> tuple[str, str]:
    if not scores:
        return "Other", "NEEDS_REVIEW"

    ranked = sorted(
        scores.items(),
        key=lambda item: (len(item[1]), max(len(phrase) for phrase in item[1])),
        reverse=True,
    )
    top_category, top_phrases = ranked[0]
    if len(ranked) > 1:
        second_category, second_phrases = ranked[1]
        if len(top_phrases) == len(second_phrases):
            return "Other", "NEEDS_REVIEW"
    return top_category, ""


def _build_reason(
    category: str,
    priority: str,
    description: str,
    category_phrases: list[str],
    severity_matches: list[str],
    flag: str,
) -> str:
    if not description:
        return "Description is missing or insufficient to classify this complaint."

    cited = category_phrases[:2] if category_phrases else []
    if not cited and category == "Other":
        cited = [description.split(".")[0].strip()]

    phrase_text = ", ".join(f'"{p}"' for p in cited) if cited else "the description"
    reason = f'Classified as {category} based on {phrase_text} in the description'

    if priority == "Urgent" and severity_matches:
        reason += f', and marked Urgent due to severity keywords: {", ".join(severity_matches)}'
    elif priority == "Urgent":
        reason += " and marked Urgent due to severity indicators in the description"
    else:
        reason += f" with {priority} priority"

    if flag == "NEEDS_REVIEW":
        reason += "; category is ambiguous and needs human review"

    return reason + "."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = _description_text(row)

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or insufficient to classify this complaint.",
            "flag": "NEEDS_REVIEW",
        }

    severity_matches = _find_severity_matches(description)
    priority = "Urgent" if severity_matches else "Standard"

    scores = _score_categories(description)
    category, flag = _pick_category(scores)
    category_phrases = scores.get(category, []) if category != "Other" else []

    reason = _build_reason(
        category, priority, description, category_phrases, severity_matches, flag
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.
    """
    results: list[dict] = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Processing failed for this row: {exc}",
                    "flag": "NEEDS_REVIEW",
                }

            if result["category"] not in ALLOWED_CATEGORIES:
                result["category"] = "Other"
                result["flag"] = "NEEDS_REVIEW"
                result["reason"] = (
                    f'Invalid category produced; flagged for review. Original description: '
                    f'{_description_text(row) or "[empty]"}'
                )

            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
