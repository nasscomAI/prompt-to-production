"""
UC-0A — Complaint Classifier

Classifies complaints using the rules defined in agents.md and skills.md.
"""

import argparse
import csv


CATEGORIES = {
    "Pothole": [
        "pothole", "road damage", "road damaged", "road hole",
        "crater", "broken road"
    ],
    "Flooding": [
        "flood", "flooding", "waterlogging", "water logged",
        "waterlogged", "water accumulation", "standing water"
    ],
    "Garbage": [
        "garbage", "trash", "waste", "litter", "dump",
        "rubbish", "uncollected waste"
    ],
    "Streetlight": [
        "streetlight", "street light", "lamp post", "lamp",
        "light pole", "lights are out", "street lights"
    ],
    "Water Supply": [
        "water supply", "no water", "water shortage",
        "water connection", "water pressure", "tap water",
        "drinking water"
    ],
    "Electricity": [
        "electricity", "power cut", "power outage", "blackout",
        "no power", "electric supply", "electricity supply"
    ],
}


URGENT_KEYWORDS = [
    "injury",
    "injured",
    "bleeding",
    "life threatening",
    "life-threatening",
    "death",
    "dying",
    "electrocution",
    "fire",
    "explosion",
    "child",
    "children",
    "school",
    "hospital",
    "ambulance",
    "immediate danger",
]


HIGH_KEYWORDS = [
    "dangerous",
    "danger",
    "major damage",
    "severe damage",
    "serious",
    "repeated",
    "blocked",
    "completely blocked",
    "days without",
    "weeks without",
]


def get_description(row: dict) -> str:
    """Safely retrieve and normalize the complaint description."""
    description = row.get("description", "")

    if description is None:
        return ""

    return str(description).strip()


def determine_category(description: str) -> tuple[str, bool]:
    """
    Determine complaint category from description.

    Returns:
        (category, needs_review)
    """
    text = description.lower()

    matches = []

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in text:
                matches.append(category)
                break

    if not matches:
        return "Other", True

    if len(set(matches)) > 1:
        return "Other", True

    return matches[0], False


def determine_priority(description: str) -> tuple[str, bool]:
    """
    Determine priority from explicit evidence in the description.

    Returns:
        (priority, needs_review)
    """
    text = description.lower()

    for keyword in URGENT_KEYWORDS:
        if keyword in text:
            return "Urgent", False

    for keyword in HIGH_KEYWORDS:
        if keyword in text:
            return "High", False

    return "Normal", False


def build_reason(
    description: str,
    category: str,
    priority: str,
    needs_review: bool
) -> str:
    """Build a reason grounded in the complaint description."""

    if not description:
        return "Description is missing or empty; classification requires review."

    if needs_review:
        if category == "Other":
            return (
                f"Description: '{description}'. No single supported category "
                "can be determined reliably from the description."
            )

        return (
            f"Description: '{description}'. The available information is "
            "ambiguous and requires review."
        )

    text = description.lower()

    matched_category_keyword = None

    for keyword in CATEGORIES.get(category, []):
        if keyword in text:
            matched_category_keyword = keyword
            break

    if priority == "Urgent":
        matched_priority_keyword = next(
            (
                keyword
                for keyword in URGENT_KEYWORDS
                if keyword in text
            ),
            None,
        )

        return (
            f"Category '{category}' based on '{matched_category_keyword}'. "
            f"Priority '{priority}' based on '{matched_priority_keyword}'."
        )

    if priority == "High":
        matched_priority_keyword = next(
            (
                keyword
                for keyword in HIGH_KEYWORDS
                if keyword in text
            ),
            None,
        )

        return (
            f"Category '{category}' based on '{matched_category_keyword}'. "
            f"Priority '{priority}' based on '{matched_priority_keyword}'."
        )

    return (
        f"Category '{category}' based on '{matched_category_keyword}'. "
        "No explicit urgent or high-priority indicator was found, "
        "so priority is Normal."
    )


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns:
        dict with keys:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = str(row.get("complaint_id", "")).strip()
    description = get_description(row)

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Normal",
            "reason": "Description is missing or empty; classification requires review.",
            "flag": "NEEDS_REVIEW",
        }

    category, category_review = determine_category(description)
    priority, priority_review = determine_priority(description)

    needs_review = category_review or priority_review

    reason = build_reason(
        description,
        category,
        priority,
        needs_review,
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW" if needs_review else "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results CSV.

    Individual bad rows are converted into NEEDS_REVIEW rows instead of
    stopping the entire batch.
    """

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(input_path, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(
                outfile,
                fieldnames=output_fields,
            )

            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception as exc:
                    complaint_id = str(
                        row.get("complaint_id", "")
                    ).strip()

                    result = {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Normal",
                        "reason": (
                            f"Row could not be classified safely: "
                            f"{type(exc).__name__}."
                        ),
                        "flag": "NEEDS_REVIEW",
                    }

                writer.writerow(result)


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

    print(f"Done. Results written to {args.output}")
