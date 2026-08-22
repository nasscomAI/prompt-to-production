"""
UC-0A — Complaint Classifier

Deterministic civic complaint classifier implementing the rules
defined in agents.md and skills.md.
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

URGENT_TRIGGERS = [
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


# Category rules are ordered deliberately.
# The first matching category wins.
CATEGORY_RULES = [
    (
        "Flooding",
        [
            r"\bflood(?:ed|ing|s)?\b",
            r"\bwaterlogged\b",
            r"\bwater logging\b",
            r"\bstanding water\b",
            r"\bsubmerged\b",
            r"\binaccessible\b",
        ],
    ),
    (
        "Pothole",
        [
            r"\bpothole(?:s)?\b",
        ],
    ),
    (
        "Streetlight",
        [
            r"\bstreetlights?\b",
            r"\bstreet lights?\b",
            r"\blamp post\b",
            r"\blamp posts\b",
        ],
    ),
    (
        "Road Damage",
        [
            r"\broad surface\b",
            r"\bdamaged road\b",
            r"\bbroken road\b",
            r"\bcracked road\b",
            r"\broad.*\bcracked\b",
            r"\broad.*\bsinking\b",
            r"\broad.*\bdamage\b",
            r"\bfootpath\b",
            r"\bfootpath tiles?\b",
            r"\bpavement\b",
            r"\btiles?\b.*\bbroken\b",
            r"\btiles?\b.*\bupturned\b",
        ],
    ),
    (
        "Drain Blockage",
        [
            r"\bblocked drain\b",
            r"\bclogged drain\b",
            r"\bdrain blockage\b",
            r"\bdrainage blockage\b",
        ],
    ),
    (
        "Waste",
        [
            r"\bgarbage\b",
            r"\bwaste\b",
            r"\btrash\b",
            r"\brubbish\b",
            r"\blitter\b",
            r"\bdump(?:ed|ing)?\b",
            r"\bdead animal\b",
            r"\bdead animals\b",
        ],
    ),
    (
        "Noise",
        [
            r"\bnoise\b",
            r"\bloudspeaker\b",
            r"\bloud music\b",
            r"\bmusic\b",
            r"\bhonking\b",
        ],
    ),
    (
        "Heritage Damage",
        [
            r"\bheritage\b",
            r"\bmonument\b",
            r"\bhistorical building\b",
            r"\bhistoric building\b",
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
]


def normalize(text: str) -> str:
    """Normalize whitespace and case for reliable matching."""
    return re.sub(r"\s+", " ", text.lower().strip())


def find_trigger(text: str):
    """Return the first urgent trigger found."""
    normalized = normalize(text)

    for trigger in URGENT_TRIGGERS:
        if re.search(r"\b" + re.escape(trigger) + r"\b", normalized):
            return trigger

    return None


def classify_category(description: str):
    """
    Determine the category from explicit evidence in the description.

    Returns:
        (category, evidence)
    """
    text = normalize(description)

    for category, patterns in CATEGORY_RULES:
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return category, match.group(0)

    return "Other", None


def classify_complaint(row: dict) -> dict:
    """
    Classify one complaint.

    Returns:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = str(row.get("complaint_id", "") or "").strip()
    description = str(row.get("description", "") or "").strip()

    # Missing description.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Complaint description is missing or empty.",
            "flag": "NEEDS_REVIEW",
        }

    category, category_evidence = classify_category(description)
    urgent_trigger = find_trigger(description)

    # Priority is determined independently of category.
    if urgent_trigger:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Unknown/ambiguous category requires human review.
    if category == "Other":
        reason = (
            "No allowed category can be determined reliably from the "
            "complaint description."
        )
        flag = "NEEDS_REVIEW"
    else:
        reason = (
            f"Category '{category}' is supported by the evidence "
            f"'{category_evidence}'."
        )
        flag = ""

    if urgent_trigger:
        reason += (
            f" Priority is Urgent because the description contains "
            f"the urgent trigger '{urgent_trigger}'."
        )

    result = {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

    # Final validation.
    if result["category"] not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"

    if result["priority"] not in {"Urgent", "Standard", "Low"}:
        result["priority"] = "Standard"
        result["flag"] = "NEEDS_REVIEW"

    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify every row, and write results CSV.

    An invalid individual row does not stop the entire batch.
    """

    results = []

    with open(
        input_path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as infile:

        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")

        required_fields = {"complaint_id", "description"}

        missing_fields = required_fields - set(reader.fieldnames)

        if missing_fields:
            raise ValueError(
                f"Input CSV is missing required fields: "
                f"{', '.join(sorted(missing_fields))}"
            )

        for row in reader:
            try:
                results.append(classify_complaint(row))

            except Exception as exc:
                results.append(
                    {
                        "complaint_id": str(
                            row.get("complaint_id", "") or ""
                        ).strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": (
                            "Row could not be classified safely: "
                            f"{exc}"
                        ),
                        "flag": "NEEDS_REVIEW",
                    }
                )

    fieldnames = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier"
    )

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

    batch_classify(
        args.input,
        args.output,
    )

    print(
        f"Done. Results written to {args.output}"
    )
