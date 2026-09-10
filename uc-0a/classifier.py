#!/usr/bin/env python3

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# ============================================================
# UC-0A Classification Schema
# ============================================================

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

ALLOWED_PRIORITIES = [
    "Urgent",
    "Standard",
    "Low",
]

ALLOWED_FLAGS = {
    "",
    "NEEDS_REVIEW",
}

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


# ============================================================
# Category vocabulary
# ============================================================
# These are classification signals, not additional categories.
# The output category is ALWAYS one of ALLOWED_CATEGORIES.

CATEGORY_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "Pothole": (
        "pothole",
        "potholes",
        "pot hole",
        "pot holes",
    ),
    "Flooding": (
        "flood",
        "flooding",
        "flooded",
        "waterlogging",
        "water logged",
        "water-logged",
        "inundated",
        "inundation",
    ),
    "Streetlight": (
        "streetlight",
        "street light",
        "streetlights",
        "street lights",
        "lamp post",
        "lamp-post",
        "lamp",
        "lighting",
        "light pole",
        "lightpole",
    ),
    "Waste": (
        "garbage",
        "trash",
        "waste",
        "rubbish",
        "litter",
        "dumping",
        "dumped",
        "dump",
        "bin",
        "bins",
        "refuse",
        "uncollected garbage",
        "uncollected waste",
    ),
    "Noise": (
        "noise",
        "noisy",
        "loud",
        "loudspeaker",
        "loudspeaker",
        "sound pollution",
        "noise pollution",
    ),
    "Road Damage": (
        "road damage",
        "damaged road",
        "road is damaged",
        "broken road",
        "road broken",
        "cracked road",
        "crack in road",
        "road crack",
        "road surface",
        "road deterioration",
        "road deteriorated",
        "damaged pavement",
        "broken pavement",
        "pavement damage",
    ),
    "Heritage Damage": (
        "heritage",
        "heritage site",
        "heritage building",
        "historic building",
        "historical building",
        "monument",
        "monuments",
        "historic monument",
        "historical monument",
        "protected monument",
        "heritage structure",
    ),
    "Heat Hazard": (
        "heat hazard",
        "extreme heat",
        "heatwave",
        "heat wave",
        "heat",
        "very hot",
        "hot weather",
        "scorching",
        "high temperature",
        "temperature hazard",
    ),
    "Drain Blockage": (
        "drain blockage",
        "blocked drain",
        "drain blocked",
        "blocked drainage",
        "drain clogged",
        "clogged drain",
        "drain clog",
        "drainage blockage",
        "blocked sewer",
        "sewer blockage",
    ),
}


# ============================================================
# Exceptions
# ============================================================

class ClassificationError(Exception):
    """Base exception for classification failures."""


class InvalidInputError(ClassificationError):
    """Raised when complaint input is invalid."""


class ValidationError(ClassificationError):
    """Raised when a classification violates enforcement rules."""


# ============================================================
# Utility functions
# ============================================================

def normalize_text(value: str) -> str:
    """Normalize whitespace without changing the substantive wording."""
    return re.sub(r"\s+", " ", str(value or "")).strip()


def contains_keyword(text: str, keyword: str) -> bool:
    """
    Case-insensitive keyword matching.

    Word boundaries prevent false matches such as:
    'fire' matching 'firewall'.
    """
    pattern = r"(?<!\w)" + re.escape(keyword.casefold()) + r"(?!\w)"
    return re.search(pattern, text.casefold()) is not None


def find_severity_keywords(description: str) -> List[str]:
    """Return severity keywords explicitly present in the description."""
    return [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if contains_keyword(description, keyword)
    ]


def find_category_matches(description: str) -> Dict[str, List[str]]:
    """
    Return category -> matched source words/phrases.

    Only allowed categories are considered.
    """
    matches: Dict[str, List[str]] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        found = [
            keyword
            for keyword in keywords
            if contains_keyword(description, keyword)
        ]

        if found:
            matches[category] = found

    return matches


def choose_best_category(
    description: str,
) -> Tuple[str, List[str], bool]:
    """
    Determine the category using deterministic keyword evidence.

    Returns:
        category
        evidence terms
        genuinely_ambiguous

    A tie between distinct categories is treated as ambiguous.
    No new category is ever invented.
    """
    matches = find_category_matches(description)

    if not matches:
        return "Other", [], True

    # Score exact keyword evidence.
    scores: Dict[str, int] = {}

    for category, terms in matches.items():
        score = 0

        for term in terms:
            # Longer/more specific phrases receive more weight.
            score += max(1, len(term.split()))

            # Exact category-name evidence is particularly strong.
            if term.casefold() == category.casefold():
                score += 2

        scores[category] = score

    highest = max(scores.values())
    winners = [
        category
        for category, score in scores.items()
        if score == highest
    ]

    if len(winners) > 1:
        # Deterministic fallback category, but mark for review.
        chosen = sorted(winners)[0]
        evidence = matches[chosen]
        return chosen, evidence, True

    chosen = winners[0]
    return chosen, matches[chosen], False


def choose_priority(description: str) -> str:
    """
    Enforcement:
    Any severity keyword MUST produce Urgent.
    """
    severity_matches = find_severity_keywords(description)

    if severity_matches:
        return "Urgent"

    # No severity keyword means no automatic Urgent classification.
    # Standard is the conservative normal priority.
    return "Standard"


def make_reason(
    description: str,
    category: str,
    evidence: List[str],
    severity_matches: List[str],
) -> str:
    """
    Generate exactly one sentence.

    The quoted evidence is copied directly from the complaint
    description so the reason is always grounded in source text.
    """

    if evidence:
        quoted = evidence[0]
    elif severity_matches:
        quoted = severity_matches[0]
    else:
        # Use a short exact fragment from the source description.
        words = description.split()
        quoted = " ".join(words[:min(6, len(words))])

    if not quoted:
        raise InvalidInputError(
            "Cannot create a description-grounded reason."
        )

    # Remove sentence-ending punctuation from the evidence so that
    # quoted complaint text cannot accidentally create another sentence.
    quoted = quoted.strip().rstrip(".!?")

    if not quoted:
        raise InvalidInputError(
            "Cannot create a description-grounded reason."
        )

    if category == "Other":
        return (
            f'The description mentions "{quoted}", '
            "but it does not clearly match a defined complaint category."
        )

    return (
        f'The description mentions "{quoted}", '
        f"supporting the {category} category."
    )

def validate_reason(reason: str, description: str) -> None:
    """
    Validate the UC-0A reason.

    A reason must:
      1. Exist.
      2. Contain exactly one sentence.
      3. Quote specific text from the complaint description.

    Punctuation inside quoted complaint text is ignored when counting
    sentences because the quoted text belongs to the source description,
    not to the generated explanation.
    """

    reason = normalize_text(reason)

    if not reason:
        raise ValidationError("Reason is missing.")

    # --------------------------------------------------------
    # Extract quoted evidence first.
    # --------------------------------------------------------

    quoted_matches = re.findall(r'"([^"]+)"', reason)

    if not quoted_matches:
        raise ValidationError(
            "Reason must cite specific words from the complaint description."
        )

    # --------------------------------------------------------
    # Verify the quoted evidence actually occurs in the source.
    # --------------------------------------------------------

    description_lower = description.casefold()

    if not any(
        quote.casefold() in description_lower
        for quote in quoted_matches
    ):
        raise ValidationError(
            "Reason does not cite words found in the complaint description."
        )

    # --------------------------------------------------------
    # Remove quoted source text before checking sentence count.
    #
    # Example:
    # The description mentions "road damaged. Very dangerous",
    # supporting the Road Damage category.
    #
    # The period inside the quote must NOT count as another sentence.
    # --------------------------------------------------------

    sentence_text = re.sub(
        r'"[^"]*"',
        '""',
        reason,
    )

    # Count sentence-ending punctuation outside quotes.
    punctuation = re.findall(r"[.!?]", sentence_text)

    if len(punctuation) != 1:
        raise ValidationError(
            "Reason must contain exactly one sentence."
        )

    # The single sentence-ending punctuation must be the final
    # non-whitespace character.
    if reason[-1] not in ".!?":
        raise ValidationError(
            "Reason must contain exactly one sentence."
        )
def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """
    Skill:
        classify_complaint

    Input:
        One complaint row containing a description.

    Output:
        category + priority + reason + flag

    Error handling:
        - Invalid description -> reject.
        - Ambiguous category -> NEEDS_REVIEW.
        - Unknown category -> Other.
        - Severity keyword -> Urgent.
        - Missing justification -> reject validation.
        - No invented subcategories.
    """

    if not isinstance(row, dict):
        raise InvalidInputError(
            "Complaint row must be a dictionary."
        )

    # Prefer the expected "description" column but support common
    # equivalent column names without changing the classification schema.
    description = ""

    for field in (
        "description",
        "Description",
        "complaint",
        "Complaint",
        "complaint_description",
        "Complaint Description",
    ):
        if field in row:
            description = normalize_text(row[field])
            if description:
                break

    if not description:
        raise InvalidInputError(
            "Complaint row has a missing or empty description."
        )

    category, evidence, ambiguous = choose_best_category(description)

    priority = choose_priority(description)

    severity_matches = find_severity_keywords(description)

    reason = make_reason(
        description=description,
        category=category,
        evidence=evidence,
        severity_matches=severity_matches,
    )

    flag = "NEEDS_REVIEW" if ambiguous else ""

    result = {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

    validate_classification(
        description=description,
        result=result,
    )

    return result


# ============================================================
# Classification validation
# ============================================================

def validate_classification(
    description: str,
    result: Dict[str, str],
) -> None:
    """
    Validate every enforcement rule applicable to one classification.
    """

    category = result.get("category", "")
    priority = result.get("priority", "")
    reason = result.get("reason", "")
    flag = result.get("flag", "")

    # Exact category strings only.
    if category not in ALLOWED_CATEGORIES:
        raise ValidationError(
            f"Invalid category: {category!r}"
        )

    # Exact priority strings only.
    if priority not in ALLOWED_PRIORITIES:
        raise ValidationError(
            f"Invalid priority: {priority!r}"
        )

    # Exact flag values only.
    if flag not in ALLOWED_FLAGS:
        raise ValidationError(
            f"Invalid flag: {flag!r}"
        )

    # Severity blindness prevention.
    severity_matches = find_severity_keywords(description)

    if severity_matches and priority != "Urgent":
        raise ValidationError(
            "Severity keyword(s) require Urgent priority: "
            + ", ".join(severity_matches)
        )

    # Reason must be present and grounded in the description.
    validate_reason(reason, description)

    # If the category is genuinely ambiguous, the flag is mandatory.
    _, _, ambiguous = choose_best_category(description)

    if ambiguous and flag != "NEEDS_REVIEW":
        raise ValidationError(
            "Genuinely ambiguous complaint must have NEEDS_REVIEW."
        )

    # Never allow an invalid invented category.
    if category not in ALLOWED_CATEGORIES:
        raise ValidationError(
            "Classification contains a category outside the allowed taxonomy."
        )


# ============================================================
# Skill: batch_classify
# ============================================================

def batch_classify(
    input_path: str | Path,
    output_path: str | Path,
) -> None:
    """
    Skill:
        batch_classify

    Reads CSV, applies classify_complaint to every row, validates all
    classifications, and writes the resulting CSV.

    The input rows are never silently dropped.
    """

    input_file = Path(input_path)
    output_file = Path(output_path)

    # ----------------------------
    # Invalid input handling
    # ----------------------------

    if not input_file.exists():
        raise InvalidInputError(
            f"Input CSV does not exist: {input_file}"
        )

    if not input_file.is_file():
        raise InvalidInputError(
            f"Input path is not a file: {input_file}"
        )

    if input_file.suffix.lower() != ".csv":
        raise InvalidInputError(
            "Input must be a CSV file."
        )

    try:
        with input_file.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)

            if reader.fieldnames is None:
                raise InvalidInputError(
                    "CSV has no header row."
                )

            if not reader.fieldnames:
                raise InvalidInputError(
                    "CSV has no columns."
                )

            rows = list(reader)

    except UnicodeDecodeError as exc:
        raise InvalidInputError(
            "CSV is not valid UTF-8 text."
        ) from exc
    except csv.Error as exc:
        raise InvalidInputError(
            f"Malformed CSV: {exc}"
        ) from exc
    except OSError as exc:
        raise InvalidInputError(
            f"Unable to read input CSV: {input_file}"
        ) from exc

    if not rows:
        raise InvalidInputError(
            "Input CSV contains no complaint rows."
        )

    # Find description column.
    description_column = None

    for candidate in (
        "description",
        "Description",
        "complaint",
        "Complaint",
        "complaint_description",
        "Complaint Description",
    ):
        if candidate in reader.fieldnames:
            description_column = candidate
            break

    if description_column is None:
        raise InvalidInputError(
            "CSV does not contain a complaint description column."
        )

    classified_rows: List[Dict[str, str]] = []

    # ----------------------------
    # Classify every row
    # ----------------------------

    for row_number, row in enumerate(rows, start=2):
        try:
            classification = classify_complaint(row)
        except ClassificationError as exc:
            raise ClassificationError(
                f"Row {row_number}: {exc}"
            ) from exc

        # Preserve every original input column.
        output_row = dict(row)

        # The UC says category and priority_flag are stripped from input,
        # but remove stale values if they happen to exist.
        output_row.pop("category", None)
        output_row.pop("priority_flag", None)

        output_row["category"] = classification["category"]
        output_row["priority"] = classification["priority"]
        output_row["reason"] = classification["reason"]
        output_row["flag"] = classification["flag"]

        classified_rows.append(output_row)

    # ----------------------------
    # Batch-level validation
    # ----------------------------

    if len(classified_rows) != len(rows):
        raise ValidationError(
            "Row integrity failure: an input complaint row was dropped."
        )

    for index, row in enumerate(classified_rows, start=2):
        description = normalize_text(row.get(description_column, ""))

        if not description:
            raise ValidationError(
                f"Row {index}: missing description after classification."
            )

        validate_classification(
            description=description,
            result={
                "category": row["category"],
                "priority": row["priority"],
                "reason": row["reason"],
                "flag": row["flag"],
            },
        )

    # ----------------------------
    # Write output
    # ----------------------------

    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Preserve original columns and append the required classification fields.
    output_fields = [
        field
        for field in reader.fieldnames
        if field not in {"category", "priority_flag", "priority", "reason", "flag"}
    ]

    output_fields.extend([
        "category",
        "priority",
        "reason",
        "flag",
    ])

    try:
        with output_file.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=output_fields,
                extrasaction="ignore",
            )

            writer.writeheader()

            for row in classified_rows:
                writer.writerow(row)

    except OSError as exc:
        raise ClassificationError(
            f"Unable to write output CSV: {output_file}"
        ) from exc


# ============================================================
# CLI
# ============================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="UC-0A City Complaint Classifier"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input complaint CSV file.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output classified CSV file.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        batch_classify(
            input_path=args.input,
            output_path=args.output,
        )

        print(
            f"Classification completed successfully: {args.output}"
        )

        return 0

    except ClassificationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    except Exception as exc:
        # Fail closed rather than producing a potentially invalid result.
        print(
            f"ERROR: unexpected failure: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())