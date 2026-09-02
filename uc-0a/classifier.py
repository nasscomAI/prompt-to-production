#!/usr/bin/env python3
"""
UC-0A — Complaint Classifier

Reads a CSV file containing a required "description" column, classifies
each complaint into one of a fixed set of categories with a priority,
a one-sentence evidence-based reason, and a review flag, then writes
the augmented rows to an output CSV.

Usage:
    python classifier.py --input INPUT.csv --output OUTPUT.csv
"""

import argparse
import csv
import re
import sys


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DESCRIPTION_COLUMN = "description"

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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

NEEDS_REVIEW = "NEEDS_REVIEW"

OUTPUT_COLUMNS = ["category", "priority", "reason", "flag"]

URGENT_KEYWORDS = [
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
    "Pothole": [
        "pothole",
        "potholes",
        "pot hole",
        "pot holes",
    ],
    "Flooding": [
        "flood",
        "floods",
        "flooding",
        "flooded",
        "waterlogged",
        "waterlogging",
        "water logged",
        "water logging",
        "standing water",
        "overflowing water",
        "inundated",
    ],
    "Streetlight": [
        "streetlight",
        "streetlights",
        "street light",
        "street lights",
        "lamp post",
        "lamp posts",
        "lamppost",
        "lampposts",
        "street lamp",
        "street lamps",
    ],
    "Waste": [
        "garbage",
        "trash",
        "waste",
        "litter",
        "littering",
        "dumping",
        "dump",
        "rubbish",
        "overflowing bin",
        "overflowing bins",
        "dead animal",
        "dead animals",
        "animal",
        "animals",
    ],
    "Noise": [
        "noise",
        "noisy",
        "loud music",
        "loud",
        "music",
        "honking",
        "horn honking",
        "blaring",
        "disturbance",
    ],
    "Road Damage": [
        "road damage",
        "damaged road",
        "broken road",
        "cracked road",
        "road crack",
        "road cracks",
        "road is broken",
        "uneven road",
        "road surface",
        "footpath",
        "footpaths",
        "footpath tiles",
        "tiles broken",
        "broken tiles",
    ],
    "Heritage Damage": [
        "heritage",
        "monument",
        "historic building",
        "historic site",
        "heritage site",
        "heritage building",
        "statue damaged",
        "ancient structure",
    ],
    "Heat Hazard": [
        "heat hazard",
        "heatwave",
        "heat wave",
        "extreme heat",
        "sunstroke",
        "heat stroke",
        "overheating",
        "scorching heat",
    ],
    "Drain Blockage": [
        "drain blockage",
        "blocked drain",
        "blocked drains",
        "clogged drain",
        "clogged drains",
        "drain is blocked",
        "drains are blocked",
        "drainage blocked",
        "sewer overflow",
        "sewage overflow",
        "clogged sewer",
        "drain",
        "drains",
        "drainage",
        "manhole",
        "manholes",
        "manhole cover",
        "manhole cover missing",
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_matches(text, keywords):
    """Return matched keywords/phrases in original case."""
    matches = []

    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            matches.append(match.group(0))

    return matches


def _find_urgent_matches(text):
    return _find_matches(text, URGENT_KEYWORDS)


def _score_categories(text):
    """Return category -> matched evidence phrases."""
    results = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = _find_matches(text, keywords)

        if matches:
            results[category] = matches

    return results


def _join_phrases(phrases):
    """Format matched phrases as a readable quoted list."""
    quoted = ["'{}'".format(phrase) for phrase in phrases]

    if len(quoted) == 1:
        return quoted[0]

    if len(quoted) == 2:
        return " and ".join(quoted)

    return ", ".join(quoted[:-1]) + ", and " + quoted[-1]


def _safe_evidence_snippet(text, max_length=60):
    """
    Create evidence text for a reason without allowing punctuation
    from the original complaint to create extra sentences.
    """
    snippet = text.strip()

    if len(snippet) > max_length:
        snippet = snippet[:max_length - 3] + "..."

    # Remove sentence-ending punctuation from the evidence snippet.
    snippet = re.sub(r"[.!?]+", "", snippet)

    return snippet


# ---------------------------------------------------------------------------
# Core classification
# ---------------------------------------------------------------------------

def classify_complaint(row):
    """
    Classify a single complaint row.

    Returns:
        dict with keys:
        category, priority, reason, flag
    """

    raw_description = row.get(DESCRIPTION_COLUMN)

    description = (
        ""
        if raw_description is None
        else str(raw_description).strip()
    )

    # Empty description
    if description == "":
        return {
            "category": "Other",
            "priority": "Low",
            "reason": (
                "The description field is empty, so there is no evidence "
                "available to classify this complaint."
            ),
            "flag": NEEDS_REVIEW,
        }

    # Urgent severity check
    urgent_matches = _find_urgent_matches(description)
    is_urgent = bool(urgent_matches)

    # Category evidence
    category_matches = _score_categories(description)

    best_category = None
    tie = False
    top_categories = []

    if category_matches:
        scored = [
            (category, len(matches))
            for category, matches in category_matches.items()
        ]

        scored.sort(key=lambda item: item[1], reverse=True)

        top_score = scored[0][1]

        top_categories = [
            category
            for category, score in scored
            if score == top_score
        ]

        if len(top_categories) == 1:
            best_category = top_categories[0]
        elif "Flooding" in top_categories:
            # Flooding evidence is treated as at least as relevant as any
            # other tied category (e.g. Drain Blockage), so resolve the
            # tie in favor of Flooding rather than falling back to Other.
            best_category = "Flooding"
        else:
            tie = True

    urgent_clause = ""

    if is_urgent:
        urgent_clause = (
            " and has Urgent priority due to the word {}".format(
                _join_phrases(
                    sorted(
                        set(urgent_matches),
                        key=str.lower
                    )
                )
            )
        )

    # -----------------------------------------------------------------------
    # Clear category
    # -----------------------------------------------------------------------

    if best_category is not None and not tie:
        matched_phrases = category_matches[best_category]

        priority = "Urgent" if is_urgent else "Standard"

        reason = (
            "The description mentions {}, which is clear evidence of a "
            "{} complaint{}."
        ).format(
            _join_phrases(
                sorted(
                    set(matched_phrases),
                    key=str.lower
                )
            ),
            best_category,
            urgent_clause,
        )

        return {
            "category": best_category,
            "priority": priority,
            "reason": reason,
            "flag": "",
        }

    # -----------------------------------------------------------------------
    # Ambiguous category
    # -----------------------------------------------------------------------

    if tie:
        involved = ", ".join(
            "{} ({})".format(
                category,
                _join_phrases(
                    sorted(
                        set(category_matches[category]),
                        key=str.lower
                    )
                ),
            )
            for category in top_categories
        )

        priority = "Urgent" if is_urgent else "Low"

        reason = (
            "The description contains evidence for more than one category "
            "({}), so it cannot be confidently assigned a single category "
            "and is classified as Other pending review{}."
        ).format(
            involved,
            urgent_clause,
        )

        return {
            "category": "Other",
            "priority": priority,
            "reason": reason,
            "flag": NEEDS_REVIEW,
        }

    # -----------------------------------------------------------------------
    # No recognizable category evidence
    # -----------------------------------------------------------------------

    priority = "Urgent" if is_urgent else "Low"

    snippet = _safe_evidence_snippet(description)

    reason = (
        "The description ('{}') does not contain any recognizable category "
        "keywords, so it cannot be confidently classified and is marked "
        "Other pending review{}."
    ).format(
        snippet,
        urgent_clause,
    )

    return {
        "category": "Other",
        "priority": priority,
        "reason": reason,
        "flag": NEEDS_REVIEW,
    }


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def batch_classify(input_path, output_path):
    """
    Read input CSV, classify every row, and write the original rows
    plus category, priority, reason, and flag columns to output CSV.

    Preserves original row count, order, and columns.

    Raises:
        ValueError if the required description column is missing.
    """

    with open(
        input_path,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as infile:

        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            raise ValueError(
                "Schema error: input CSV has no header row; "
                "required column 'description' cannot be located."
            )

        if DESCRIPTION_COLUMN not in reader.fieldnames:
            raise ValueError(
                "Schema error: required column 'description' "
                "not found in input CSV. Found columns: {}. "
                "Refusing to fall back to another column."
                .format(reader.fieldnames)
            )

        original_fieldnames = list(reader.fieldnames)

        output_fieldnames = original_fieldnames + [
            column
            for column in OUTPUT_COLUMNS
            if column not in original_fieldnames
        ]

        rows = []

        for row in reader:
            clean_row = {}

            # Preserve every original column.
            for column in original_fieldnames:
                value = row.get(column)
                clean_row[column] = (
                    "" if value is None else value
                )

            classification = classify_complaint(row)

            clean_row["category"] = classification["category"]
            clean_row["priority"] = classification["priority"]
            clean_row["reason"] = classification["reason"]
            clean_row["flag"] = classification["flag"]

            rows.append(clean_row)

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=output_fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "UC-0A Complaint Classifier: "
            "classify complaints from a CSV file."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file."
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the output CSV file."
    )

    args = parser.parse_args()

    try:
        count = batch_classify(
            args.input,
            args.output
        )

    except ValueError as exc:
        sys.stderr.write(
            "Error: {}\n".format(exc)
        )
        sys.exit(1)

    except FileNotFoundError as exc:
        sys.stderr.write(
            "Error: input file not found: {}\n".format(exc)
        )
        sys.exit(1)

    except Exception as exc:
        sys.stderr.write(
            "Error during classification: {}\n".format(exc)
        )
        sys.exit(1)

    sys.stdout.write(
        "Processed {} row(s). Output written to {}\n".format(
            count,
            args.output
        )
    )


if __name__ == "__main__":
    main()
