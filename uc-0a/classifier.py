"""Deterministic UC-0A citizen complaint classifier."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Iterable


FIELDNAMES = ["complaint_id", "category", "priority", "reason", "flag"]

CATEGORIES = (
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

PRIORITIES = ("Urgent", "Standard", "Low")

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

# Patterns are deliberately based only on words in the complaint description.
CATEGORY_PATTERNS: dict[str, tuple[str, ...]] = {
    "Pothole": (r"\bpotholes?\b",),
    "Flooding": (
        r"\bflooded\b",
        r"\bfloods?\b",
        r"\bflooding\b",
        r"\bwaterlog(?:ged|ging)?\b",
        r"\bknee-deep\b",
        r"\brainwater\b",
    ),
    "Streetlight": (
        r"\bstreetlights?\b",
        r"\blights? out\b",
        r"\bunlit\b",
        r"\bdarkness\b",
        r"\blamp post\b",
    ),
    "Waste": (
        r"\bwaste\b",
        r"\bgarbage\b",
        r"\brubbish\b",
        r"\btrash\b",
        r"\bdead animal\b",
        r"\bbins?\b",
    ),
    "Noise": (
        r"\bnoise\b",
        r"\bmusic\b",
        r"\bdrilling\b",
        r"\bamplifiers?\b",
        r"\bengines? on\b",
        r"\bidling\b",
    ),
    "Road Damage": (
        r"\broad (?:surface )?(?:collapsed|collapse|cracked|damaged|subsided|subsidence|buckled|sinking)\b",
        r"\broad subsidence\b",
        r"\bfootpath\b",
        r"\bmanhole cover\b",
        r"\bpav(?:ing|ement)\b",
        r"\bcobblestones?\b",
        r"\btarmac\b",
        r"\broad dividers?\b",
    ),
    "Heritage Damage": (
        r"\bheritage\b",
        r"\bhistoric\b",
        r"\bancient\b",
    ),
    "Heat Hazard": (
        r"\bheat\b",
        r"\bheatwave\b",
        r"\btemperatures?\b",
        r"\b\d{2}\s*°c\b",
        r"\bmelting\b",
        r"\bburns?\b",
        r"\bfull sun\b",
    ),
    "Drain Blockage": (
        r"\bdrains?\b.*\bblocked\b",
        r"\bblocked\b.*\bdrains?\b",
        r"\bdrain blockage\b",
    ),
}

HERITAGE_DAMAGE_PATTERNS = (
    r"\bknocked over\b",
    r"\bbroken\b",
    r"\bdamage(?:d)?\b",
    r"\bdefaced\b",
    r"\bremoved\b",
    r"\bnot replaced\b",
    r"\bsubsidence\b",
    r"\bheritage concern\b",
)

LOW_SEVERITY_PATTERNS = (
    r"\bcosmetic\b",
    r"\bminor\b",
    r"\bslight(?:ly)?\b",
    r"\bfaded\b",
)


def _first_match(description: str, patterns: Iterable[str]) -> str | None:
    """Return the exact text of the first case-insensitive pattern match."""
    for pattern in patterns:
        match = re.search(pattern, description, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def _has_match(description: str, patterns: Iterable[str]) -> bool:
    return _first_match(description, patterns) is not None


def _select_category(description: str) -> tuple[str, str | None]:
    """Return category and exact evidence from the description."""
    matches = {
        category: _first_match(description, patterns)
        for category, patterns in CATEGORY_PATTERNS.items()
    }

    # A pothole is always more specific than general road damage.
    if matches["Pothole"]:
        return "Pothole", matches["Pothole"]

    # Active inundation is the reported problem even when a blocked drain is
    # also mentioned. A blockage without active flooding remains a drain issue.
    if matches["Flooding"]:
        return "Flooding", matches["Flooding"]
    if matches["Drain Blockage"]:
        return "Drain Blockage", matches["Drain Blockage"]

    # "Heritage area" alone does not turn waste, noise, or lighting into
    # heritage damage. Both a heritage signal and damage signal are required.
    if matches["Heritage Damage"] and _has_match(
        description, HERITAGE_DAMAGE_PATTERNS
    ):
        return "Heritage Damage", matches["Heritage Damage"]

    # Explicit heat conditions take precedence over the affected surface.
    if matches["Heat Hazard"]:
        return "Heat Hazard", matches["Heat Hazard"]

    for category in ("Streetlight", "Waste", "Noise", "Road Damage"):
        if matches[category]:
            return category, matches[category]

    return "Other", None


def _select_priority(description: str) -> tuple[str, str | None]:
    urgent_evidence = _first_match(
        description,
        (rf"\b{re.escape(keyword)}\w*\b" for keyword in URGENT_KEYWORDS),
    )
    if urgent_evidence:
        return "Urgent", urgent_evidence
    if _has_match(description, LOW_SEVERITY_PATTERNS):
        return "Low", _first_match(description, LOW_SEVERITY_PATTERNS)
    return "Standard", None


def _reason(
    category: str,
    priority: str,
    category_evidence: str | None,
    priority_evidence: str | None,
    description: str,
) -> str:
    if category == "Other":
        if priority_evidence:
            return (
                f'The description contains "{priority_evidence}", requiring '
                f"{priority} priority, but provides no terms that identify an "
                "allowed complaint category."
            )
        first_clause = re.split(r"[.!?]", description, maxsplit=1)[0]
        excerpt = " ".join(first_clause.split()[:8]).strip(" ;:")
        if excerpt:
            return (
                f'The words "{excerpt}" do not identify an allowed complaint '
                f"category, so it is Other with {priority} priority."
            )
        return (
            "The empty description provides no specific terms that identify an "
            f"allowed complaint category, so it is Other with {priority} priority."
        )

    evidence = f'"{category_evidence}"'
    if priority_evidence:
        return (
            f'The words {evidence} identify {category}, while '
            f'"{priority_evidence}" requires {priority} priority.'
        )
    return (
        f"The words {evidence} identify {category}, with no mandatory urgent "
        f"keyword present, so the priority is {priority}."
    )


def classify_complaint(row: dict) -> dict:
    """Classify one complaint row using only its description."""
    if not isinstance(row, dict):
        raise TypeError("complaint row must be a dictionary")

    complaint_id = row.get("complaint_id")
    if complaint_id is None or not str(complaint_id).strip():
        raise ValueError("complaint_id is required")

    description_value = row.get("description")
    description = "" if description_value is None else str(description_value).strip()

    category, category_evidence = _select_category(description)
    priority, priority_evidence = _select_priority(description)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    result = {
        "complaint_id": str(complaint_id),
        "category": category,
        "priority": priority,
        "reason": _reason(
            category,
            priority,
            category_evidence,
            priority_evidence,
            description,
        ),
        "flag": flag,
    }
    _validate_result(result)
    return result


def _validate_result(result: dict) -> None:
    if result["category"] not in CATEGORIES:
        raise ValueError(f"invalid category: {result['category']}")
    if result["priority"] not in PRIORITIES:
        raise ValueError(f"invalid priority: {result['priority']}")
    if result["flag"] not in ("", "NEEDS_REVIEW"):
        raise ValueError(f"invalid flag: {result['flag']}")
    if not result["reason"].strip():
        raise ValueError("reason must not be blank")
    if result["category"] == "Other" and result["flag"] != "NEEDS_REVIEW":
        raise ValueError("Other complaints must be flagged NEEDS_REVIEW")


def batch_classify(input_path: str, output_path: str) -> None:
    """Classify all 15 rows in an input CSV and atomically write the output."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError("input CSV is missing a header")

        missing_columns = {"complaint_id", "description"} - set(reader.fieldnames)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"input CSV is missing required columns: {missing}")
        rows = list(reader)

    if len(rows) != 15:
        raise ValueError(f"input CSV must contain exactly 15 rows; found {len(rows)}")

    results = [classify_complaint(row) for row in rows]
    input_ids = [str(row["complaint_id"]) for row in rows]
    output_ids = [result["complaint_id"] for result in results]
    if output_ids != input_ids or len(set(output_ids)) != len(output_ids):
        raise ValueError("complaint_id values must be unique and preserved in order")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = output_file.with_name(f".{output_file.name}.tmp")
    try:
        with temporary_file.open("w", encoding="utf-8", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(results)
        temporary_file.replace(output_file)
    finally:
        if temporary_file.exists():
            temporary_file.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
