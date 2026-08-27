"""UC-0A municipal complaint classifier.

The rules in this module deliberately use only a complaint row's description.
They implement the category, urgency, evidence, and review constraints recorded
in agents.md and skills.md.
"""

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]
ALLOWED_CATEGORIES = {
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
SEVERITY_PATTERNS = (
    r"\binjur(?:y|ed)\b",
    r"\bchild(?:ren)?\b",
    r"\bschool\b",
    r"\bhospital\w*\b",
    r"\bambulance\b",
    r"\bfire\b",
    r"\bhazard\b",
    r"\bfell\b",
    r"\bcollaps\w*\b",
)

# A keyword can match only the description. The more specific patterns receive
# a higher score so, for example, a blocked drain outranks a generic reference
# to rain when drainage is the stated issue.
CATEGORY_PATTERNS = {
    "Pothole": (r"\bpotholes?\b",),
    "Flooding": (r"\bflood(?:ed|ing|s)?\b", r"\bwaterlogging\b", r"\bwater[- ]?logged\b"),
    "Streetlight": (
        r"\bstreet\s*lights?\b",
        r"\bstreetlights?\b",
        r"\blamp\s*post\b",
        r"\bunlit\b",
        r"\bdarkness\b",
    ),
    "Waste": (
        r"\bgarbage\b",
        r"\bwaste\b",
        r"\bbins?\b",
        r"\blitter\b",
        r"\bdead animal\b",
        r"\brubbish\b",
    ),
    "Noise": (r"\bnoise\b", r"\bmusic\b", r"\bamplifiers?\b", r"\bdrilling\b", r"\bband\b", r"\bidling\b"),
    "Road Damage": (
        r"\broad\s+(?:surface|collapsed|collapse|subsided|subsidence|cracked|sinking|buckled)\b",
        r"\bfootpath\b",
        r"\bpav(?:ing|ement)\b",
        r"\bcobblestones?\b",
        r"\bmanhole cover\b",
        r"\btiles?\s+(?:broken|upturned)\b",
        r"\btarmac\b",
    ),
    "Heritage Damage": (
        r"\bheritage\b.*\b(?:damag|defac|broken|removed|knocked|not restored)",
        r"\bhistoric\b.*\b(?:damag|broken|removed)",
        r"\bancient\b.*\b(?:damag|broken|subsidence)",
    ),
    "Heat Hazard": (
        r"\bheat(?:wave)?\b",
        r"\b(?:dangerous|unbearable|extreme) temperatures?\b",
        r"\b(?:melting|bubbling|burns?|overheat(?:ed|ing)?)\b",
        r"\b\d{2}\s*(?:°|Â°|degrees?\b)",
        r"\b(?:full sun|sun exposure)\b",
    ),
    "Drain Blockage": (
        r"\b(?:stormwater\s+)?drain(?:age)?\b.{0,40}\bblocked\b",
        r"\bblocked\s+(?:stormwater\s+)?drain\b",
        r"\bsewer\s+(?:is\s+)?blocked\b",
        r"\bmanhole\b.*\bblocked\b",
    ),
}


def _matches(description: str, patterns: Iterable[str]) -> List[str]:
    """Return the literal phrases that support a category."""
    return [match.group(0) for pattern in patterns if (match := re.search(pattern, description, re.I))]


def _category_and_evidence(description: str) -> Tuple[str, str, bool]:
    """Return category, supporting phrase, and whether the result is ambiguous."""
    matches = {
        category: _matches(description, patterns)
        for category, patterns in CATEGORY_PATTERNS.items()
    }
    matches = {category: phrases for category, phrases in matches.items() if phrases}
    if not matches:
        return "Other", "no clear category-specific words", True

    # Heritage describes the object being damaged, so it wins only when its
    # physical-damage pattern matches; mentions of a heritage area alone do not
    # turn a waste or noise complaint into Heritage Damage.
    if "Heritage Damage" in matches:
        return "Heritage Damage", matches["Heritage Damage"][0], False

    # A specifically blocked drain is more precise than a resulting flood.
    if "Drain Blockage" in matches:
        return "Drain Blockage", matches["Drain Blockage"][0], False

    # Otherwise, use the first matching category in this stable priority order.
    priority_order = (
        "Pothole",
        "Flooding",
        "Streetlight",
        "Waste",
        "Noise",
        "Heat Hazard",
        "Road Damage",
    )
    selected = next(category for category in priority_order if category in matches)
    unrelated_matches = set(matches) - {selected}
    # A single report may mention a hazard or a location associated with another
    # service. Flag only competing service problems, not severity language.
    ambiguous = bool(
        unrelated_matches and selected not in {"Flooding", "Road Damage", "Heat Hazard"}
    )
    return selected, matches[selected][0], ambiguous


def _severity_match(description: str) -> str:
    for pattern in SEVERITY_PATTERNS:
        match = re.search(pattern, description, re.I)
        if match:
            return match.group(0)
    return ""


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint into the required, auditable output schema."""
    complaint_id = ""
    if isinstance(row, dict):
        complaint_id = str(row.get("complaint_id") or "").strip()
        description = str(row.get("description") or "").strip()
    else:
        description = ""

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing, so no category can be determined.",
            "flag": "NEEDS_REVIEW",
        }

    category, evidence, ambiguous = _category_and_evidence(description)
    severity = _severity_match(description)
    priority = "Urgent" if severity else "Standard"
    flag = "NEEDS_REVIEW" if ambiguous else ""

    if severity:
        reason = (
            f'Classified as {category} because it mentions "{evidence}"; '
            f'priority is Urgent because it includes "{severity}".'
        )
    elif category == "Other":
        reason = "No clear category-specific words appear in the description."
    else:
        reason = f'Classified as {category} because it mentions "{evidence}".'

    return {
        "complaint_id": complaint_id,
        "category": category if category in ALLOWED_CATEGORIES else "Other",
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Classify every CSV row, writing a reviewable fallback for bad rows."""
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as input_file:
            reader = csv.DictReader(input_file)
            if not reader.fieldnames or "description" not in reader.fieldnames:
                raise ValueError("Input CSV must contain a description column.")

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8", newline="") as output_file:
                writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
                writer.writeheader()
                for row in reader:
                    try:
                        writer.writerow(classify_complaint(row))
                    except (AttributeError, TypeError, ValueError) as error:
                        writer.writerow(
                            {
                                "complaint_id": str((row or {}).get("complaint_id") or ""),
                                "category": "Other",
                                "priority": "Standard",
                                "reason": f"Row could not be classified: {error}.",
                                "flag": "NEEDS_REVIEW",
                            }
                        )
    except OSError as error:
        raise OSError(f"Unable to read input CSV '{input_path}': {error}") from error


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
