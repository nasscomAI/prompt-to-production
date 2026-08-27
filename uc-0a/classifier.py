"""
UC-0A — Complaint Classifier

Implements the rules defined in agents.md and skills.md:
- classify a single complaint row using only complaint_id and description
- output exactly: complaint_id, category, priority, reason, flag
- do not crash on malformed rows
- write one result row per input CSV row
"""

import argparse
import csv
import re
from typing import Any, Dict, Iterable, List, Tuple

APPROVED_CATEGORIES = {
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
}

APPROVED_PRIORITIES = {"Urgent", "Standard", "Low"}
OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

# Per agents.md, these exact severity keywords make priority Urgent.
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

# Category detection is intentionally keyword-based and limited to the supplied
# description text. The output category is always one of APPROVED_CATEGORIES.
CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "Pothole": [
        r"\bpothole\b",
        r"\bpot\s*hole\b",
    ],
    "Flooding": [
        r"\bflood(?:ed|ing)?\b",
        r"\bwater\s*logging\b",
        r"\bwaterlogged\b",
        r"\bstanding\s+water\b",
        r"\bwater\s+accumulation\b",
    ],
    "Streetlight": [
        r"\bstreet\s*light\b",
        r"\bstreetlight\b",
        r"\blamp\s*post\b",
        r"\blight\s*pole\b",
        r"\broad\s+light\b",
    ],
    "Waste": [
        r"\bgarbage\b",
        r"\btrash\b",
        r"\brubbish\b",
        r"\bwaste\b",
        r"\blitter\b",
        r"\bdumping\b",
        r"\bdump(?:ed)?\b",
        r"\bbin\b",
    ],
    "Noise": [
        r"\bnoise\b",
        r"\bnoisy\b",
        r"\bloud\b",
        r"\bhonking\b",
        r"\bmusic\b",
        r"\bspeaker\b",
    ],
    "Road Damage": [
        r"\broad\s+damage\b",
        r"\bdamaged\s+road\b",
        r"\bbroken\s+road\b",
        r"\bcracked\s+road\b",
        r"\broad\s+crack\b",
        r"\buneven\s+road\b",
        r"\bbroken\s+pavement\b",
        r"\bdamaged\s+pavement\b",
        r"\basphalt\b",
    ],
    "Heritage Damage": [
        r"\bheritage\b",
        r"\bmonument\b",
        r"\bhistoric\b",
        r"\bhistorical\b",
        r"\bstatue\b",
    ],
    "Heat Hazard": [
        r"\bheat\s*hazard\b",
        r"\bheatwave\b",
        r"\bheat\s+wave\b",
        r"\bextreme\s+heat\b",
        r"\bdehydration\b",
    ],
    "Drain Blockage": [
        r"\bblocked\s+drain\b",
        r"\bdrain\s+block(?:ed|age)?\b",
        r"\bclogged\s+drain\b",
        r"\bdrain(?:age)?\s+clog(?:ged)?\b",
        r"\bblocked\s+gutter\b",
        r"\bclogged\s+gutter\b",
        r"\bsewer\s+block(?:ed|age)?\b",
        r"\bblocked\s+sewer\b",
    ],
}


def _clean_text(value: Any) -> str:
    """Return a safe, printable string without changing the meaning."""
    if value is None:
        return ""
    return str(value).strip()


def _contains_severity(text: str) -> Tuple[bool, str]:
    """Return whether any required severity keyword appears in text."""
    for keyword in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", text, flags=re.IGNORECASE):
            return True, keyword
    return False, ""


def _matched_phrases(text: str, patterns: Iterable[str]) -> List[str]:
    """Return de-duplicated phrases from text that matched the given patterns."""
    matches: List[str] = []
    for pattern in patterns:
        found = re.search(pattern, text, flags=re.IGNORECASE)
        if found:
            phrase = found.group(0).strip()
            if phrase.lower() not in {m.lower() for m in matches}:
                matches.append(phrase)
    return matches


def _detect_category(description: str) -> Tuple[str, List[str], bool]:
    """
    Detect category from description only.

    Returns: category, evidence phrases, ambiguous flag.
    Ambiguous means two or more approved categories are supported by the same
    highest number of evidence matches.
    """
    category_hits: Dict[str, List[str]] = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        hits = _matched_phrases(description, patterns)
        if hits:
            category_hits[category] = hits

    if not category_hits:
        return "Other", [], True

    max_hits = max(len(hits) for hits in category_hits.values())
    top_categories = [cat for cat, hits in category_hits.items() if len(hits) == max_hits]

    if len(top_categories) > 1:
        # Genuine ambiguity: do not pretend confidence when multiple approved
        # categories are equally evidenced by the description.
        combined_evidence: List[str] = []
        for cat in top_categories:
            combined_evidence.extend(category_hits[cat])
        return "Other", combined_evidence, True

    chosen = top_categories[0]
    return chosen, category_hits[chosen], False


def _one_sentence_reason(category: str, priority: str, evidence: List[str], description: str, issue: str = "") -> str:
    """Build one sentence that cites complaint wording or explains invalid input."""
    if issue:
        if description:
            snippet = description[:80].replace("\n", " ")
            return f"{issue}; available complaint text includes '{snippet}'."
        return f"{issue}; no complaint description was available."

    if evidence:
        quoted = "', '".join(evidence[:3])
        return f"Classified as {category} because the description contains '{quoted}', with {priority} priority."

    snippet = description[:80].replace("\n", " ")
    return f"Classified as Other because the description '{snippet}' does not clearly match an approved category."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns exactly these keys: complaint_id, category, priority, reason, flag.
    This function never raises for bad row-level input.
    """
    try:
        if not isinstance(row, dict):
            available_text = _clean_text(row)
            urgent, _ = _contains_severity(available_text)
            priority = "Urgent" if urgent else "Low"
            return {
                "complaint_id": "",
                "category": "Other",
                "priority": priority,
                "reason": _one_sentence_reason(
                    "Other", priority, [], available_text, "Malformed row input"
                ),
                "flag": "NEEDS_REVIEW",
            }

        complaint_id = _clean_text(row.get("complaint_id"))
        description = _clean_text(row.get("description"))

        # If description is unavailable, still scan all available row text for
        # severity only, as required by skills.md error handling.
        available_text = " ".join(_clean_text(v) for v in row.values())
        urgent, severity = _contains_severity(description or available_text)
        priority = "Urgent" if urgent else "Low"

        if not complaint_id:
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": priority,
                "reason": _one_sentence_reason(
                    "Other", priority, [severity] if severity else [], description, "Missing or null complaint_id"
                ),
                "flag": "NEEDS_REVIEW",
            }

        if not description:
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": priority,
                "reason": _one_sentence_reason(
                    "Other", priority, [severity] if severity else [], description, "Missing or empty description"
                ),
                "flag": "NEEDS_REVIEW",
            }

        category, evidence, ambiguous = _detect_category(description)
        if urgent:
            priority = "Urgent"
        elif category == "Other":
            priority = "Low"
        else:
            priority = "Standard"

        flag = "NEEDS_REVIEW" if ambiguous else ""
        reason = _one_sentence_reason(category, priority, evidence, description)

        result = {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }

        # Final schema guardrails: never output values outside the approved schema.
        if result["category"] not in APPROVED_CATEGORIES:
            result["category"] = "Other"
            result["flag"] = "NEEDS_REVIEW"
        if result["priority"] not in APPROVED_PRIORITIES:
            result["priority"] = "Low"
            result["flag"] = "NEEDS_REVIEW"
        return {field: result.get(field, "") for field in OUTPUT_FIELDS}

    except Exception as exc:  # Defensive row-level guard: do not crash batch.
        return {
            "complaint_id": "",
            "category": "Other",
            "priority": "Low",
            "reason": f"Malformed row input caused a row-level error: {type(exc).__name__}.",
            "flag": "NEEDS_REVIEW",
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write a results CSV.

    The batch continues even if individual rows are invalid. File-level errors
    such as a missing or unreadable input file are raised clearly.
    """
    if not input_path:
        raise ValueError("input_path is required")
    if not output_path:
        raise ValueError("output_path is required")

    try:
        with open(input_path, mode="r", newline="", encoding="utf-8-sig") as input_file:
            reader = csv.DictReader(input_file)
            rows = list(reader)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input CSV not found: {input_path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to read input CSV '{input_path}': {exc}") from exc

    results: List[Dict[str, str]] = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:  # Extra safety; classify_complaint should not raise.
            complaint_id = _clean_text(row.get("complaint_id")) if isinstance(row, dict) else ""
            results.append(
                {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Malformed row input caused a row-level error: {type(exc).__name__}.",
                    "flag": "NEEDS_REVIEW",
                }
            )

    try:
        with open(output_path, mode="w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows({field: row.get(field, "") for field in OUTPUT_FIELDS} for row in results)
    except OSError as exc:
        raise OSError(f"Unable to write output CSV '{output_path}': {exc}") from exc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
