"""
UC-0A — Complaint Classifier
"""

import argparse
import csv


# Exact categories required by the workshop
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


# Any of these words must make priority Urgent
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


def classify_complaint(row: dict) -> dict:
    """
    Classify one complaint.

    Returns:
        complaint_id
        category
        priority
        reason
        flag
    """

    complaint_id = row.get("complaint_id", "")

    # Find the complaint description
    description = str(
        row.get("description")
        or row.get("complaint")
        or row.get("text")
        or ""
    ).strip()

    # Missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No complaint description was provided.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # ---------------------------------------------------------
    # PRIORITY
    # ---------------------------------------------------------

    matched_severity = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if keyword in text
    ]

    if matched_severity:
        priority = "Urgent"
    else:
        priority = "Standard"

    # ---------------------------------------------------------
    # CATEGORY
    # ---------------------------------------------------------

    category = "Other"

    if "pothole" in text:
        category = "Pothole"

    elif "flood" in text:
        category = "Flooding"

    elif (
        "streetlight" in text
        or "street light" in text
    ):
        category = "Streetlight"

    elif (
        "waste" in text
        or "garbage" in text
        or "trash" in text
        or "rubbish" in text
    ):
        category = "Waste"

    elif (
        "noise" in text
        or "music" in text
    ):
        category = "Noise"

    elif (
        "road damage" in text
        or "damaged road" in text
        or "road surface" in text
        or "cracked" in text
        or "sinking" in text
    ):
        category = "Road Damage"

    elif "heritage" in text:
        category = "Heritage Damage"

    elif "heat" in text:
        category = "Heat Hazard"

    elif (
        "drain" in text
        and (
            "block" in text
            or "blocked" in text
            or "blockage" in text
        )
    ):
        category = "Drain Blockage"

    # ---------------------------------------------------------
    # AMBIGUITY FLAG
    # ---------------------------------------------------------

    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    # ---------------------------------------------------------
    # REASON
    # ---------------------------------------------------------

    if matched_severity:
        keyword = matched_severity[0]

        reason = (
            f"Priority is Urgent because the description contains "
            f"the severity keyword '{keyword}': {description}"
        )

    else:
        reason = (
            f"Category '{category}' is based on the description: "
            f"{description}"
        )

    # Final category validation
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify every row,
    and write results to output CSV.

    Bad rows are flagged instead of stopping the program.
    """

    results = []

    try:
        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as infile:

            reader = csv.DictReader(infile)

            for row in reader:

                try:
                    result = classify_complaint(row)
                    results.append(result)

                except Exception as exc:
                    results.append({
                        "complaint_id": row.get(
                            "complaint_id", ""
                        ),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": (
                            f"Row could not be classified: {exc}"
                        ),
                        "flag": "NEEDS_REVIEW",
                    })

    except Exception as exc:

        results.append({
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": (
                f"Input file could not be processed: {exc}"
            ),
            "flag": "NEEDS_REVIEW",
        })

    # ---------------------------------------------------------
    # WRITE OUTPUT CSV
    # ---------------------------------------------------------

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
        newline="",
        encoding="utf-8"
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames
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
        help="Path to test_[city].csv"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV"
    )

    args = parser.parse_args()

    batch_classify(
        args.input,
        args.output
    )

    print(
        f"Done. Results written to {args.output}"
    )