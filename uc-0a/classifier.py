"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import csv

CATEGORIES = [
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

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns:
        dict containing complaint_id, category, priority, reason, and flag.
    """

    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")

    category = "Other"
    priority = "Standard"
    flag = ""

    if "pothole" in description:
        category = "Pothole"

    elif "flood" in description or "waterlogging" in description:
        category = "Flooding"

    elif "streetlight" in description or "light not working" in description:
        category = "Streetlight"

    elif (
        "garbage" in description
        or "waste" in description
        or "trash" in description
    ):
        category = "Waste"

    elif "noise" in description or "loud" in description:
        category = "Noise"

    elif "road" in description:
        category = "Road Damage"

    elif "heritage" in description or "monument" in description:
        category = "Heritage Damage"

    elif "heat" in description:
        category = "Heat Hazard"

    elif "drain" in description or "sewer" in description:
        category = "Drain Blockage"

    # Determine priority
    if any(keyword in description for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"

    # Create reason
    reason = (
        f"Category selected based on complaint description: "
        f"'{description[:60]}...'"
    )

    # Flag ambiguous complaints
    if category == "Other":
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
    Read input CSV, classify each row, and write results CSV.
    """

    fieldnames = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(input_path, "r", newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)

            except Exception:
                writer.writerow(
                    {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Unable to process complaint.",
                        "flag": "NEEDS_REVIEW",
                    }
                )


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

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")