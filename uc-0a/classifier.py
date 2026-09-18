"""
UC-0A — Complaint Classifier

Deterministic implementation based on agents.md and skills.md.
"""

import argparse
import csv
import re

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

SEVERITY_KEYWORDS = (
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

CATEGORY_RULES = [
    (
        "Pothole",
        [
            r"\bpotholes?\b",
        ],
    ),
    (
        "Flooding",
        [
            r"\bflood(?:ing|ed|s)?\b",
            r"\bwaterlogged\b",
            r"\bwaterlogging\b",
            r"\bwater accumulation\b",
        ],
    ),
    (
        "Drain Blockage",
        [
            r"\bblocked drain\b",
            r"\bclogged drain\b",
            r"\bdrain blockage\b",
            r"\bdrainage blockage\b",
            r"\bsewer blockage\b",
            r"\bdrainage\b",
            r"\bdrain\b",
        ],
    ),
    (
        "Streetlight",
        [
            r"\bstreet ?lights?\b",
            r"\bstreetlights?\b",
            r"\blamp ?posts?\b",
            r"\blight poles?\b",
        ],
    ),
    (
        "Waste",
        [
            r"\bwaste\b",
            r"\bgarbage\b",
            r"\btrash\b",
            r"\brubbish\b",
            r"\bdumping\b",
            r"\bdumped\b",
            r"\bbins?\b",
        ],
    ),
    (
        "Noise",
        [
            r"\bnoise\b",
            r"\bnoisy\b",
            r"\bloudspeaker\b",
            r"\bloud music\b",
            r"\bplaying music\b",
            r"\bmusic past midnight\b",
        ],
    ),
    (
        "Heritage Damage",
        [
            r"\bheritage damage\b",
            r"\bdamaged heritage\b",
            r"\bdamaged monument\b",
            r"\bmonument damage\b",
            r"\bhistoric damage\b",
            r"\bhistorical damage\b",
            r"\bprotected structure\b",
        ],
    ),
    (
        "Heat Hazard",
        [
            r"\bheatwave\b",
            r"\bheat wave\b",
            r"\bextreme heat\b",
            r"\bheat hazard\b",
        ],
    ),
    (
        "Road Damage",
        [
            r"\broad damage\b",
            r"\bdamaged road\b",
            r"\bdamaged roads\b",
            r"\bdamage to (?:the )?road\b",
            r"\broad surface\b",
            r"\bcracked road\b",
            r"\broad crack\b",
            r"\bsinking\b",
            r"\bfootpath tiles\b",
            r"\bfootpath\b.*\bbroken\b",
        ],
    ),
]


def find_category_matches(description: str) -> list[tuple[str, str]]:
    """Return all category matches and the actual matching phrase."""
    matches = []

    for category, patterns in CATEGORY_RULES:
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                matches.append((category, match.group(0)))
                break

    return matches


def find_severity_keyword(description: str) -> str | None:
    """Return the first severity keyword found, if any."""
    for keyword in SEVERITY_KEYWORDS:
        if re.search(
            rf"\b{re.escape(keyword)}\b",
            description,
            re.IGNORECASE,
        ):
            return keyword

    return None


def classify_complaint(row: dict) -> dict:
    """
    Classify one complaint.

    Returns:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    # Missing description.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is unavailable.",
            "flag": "NEEDS_REVIEW",
        }

    severity = find_severity_keyword(description)
    priority = "Urgent" if severity else "Standard"

    matches = find_category_matches(description)

    # No recognised category.
    if not matches:
        # Use a short phrase from the description so the reason remains
        # grounded in the complaint text.
        words = description.split()
        evidence = " ".join(words[:6]).rstrip(".,;:")

        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": (
                f'The description mentions "{evidence}", but no permitted '
                "category can be determined confidently."
            ),
            "flag": "NEEDS_REVIEW",
        }
    # Multiple categories = genuine ambiguity unless the text clearly
    # distinguishes one from another. We flag rather than invent certainty.
    unique_categories = []
    for category, _ in matches:
        if category not in unique_categories:
            unique_categories.append(category)

    if len(unique_categories) > 1:
        phrases = ", ".join(f'"{phrase}" ({category})' for category, phrase in matches)

        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": (
                f"The description contains multiple category indicators: " f"{phrases}."
            ),
            "flag": "NEEDS_REVIEW",
        }

    category, phrase = matches[0]

    if severity:
        reason = (
            f'The description mentions "{phrase}" and the severity keyword '
            f'"{severity}", so it is classified as {category} with Urgent priority.'
        )
    else:
        reason = (
            f'The description mentions "{phrase}", so it is classified as '
            f"{category} with Standard priority."
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify every row, and write the results CSV."""

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(
        input_path,
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as input_file:

        reader = csv.DictReader(input_file)

        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")

        required_fields = {"complaint_id", "description"}
        missing = required_fields - set(reader.fieldnames)

        if missing:
            raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

        results = []

        for row_number, row in enumerate(reader, start=2):
            try:
                result = classify_complaint(row)

            except Exception as exc:
                result = {
                    "complaint_id": (
                        str(row.get("complaint_id", "")).strip() or f"ROW-{row_number}"
                    ),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": (f"Classification failed for this row: {exc}."),
                    "flag": "NEEDS_REVIEW",
                }

            # Final safety validation.
            if result["category"] not in ALLOWED_CATEGORIES:
                result["category"] = "Other"
                result["flag"] = "NEEDS_REVIEW"

            if result["priority"] not in {"Urgent", "Standard", "Low"}:
                result["priority"] = "Standard"
                result["flag"] = "NEEDS_REVIEW"

            results.append(result)

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as output_file:

        writer = csv.DictWriter(
            output_file,
            fieldnames=output_fields,
        )

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to test_[city].csv",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV",
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")
