"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import csv


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns:
        dict with keys:
        complaint_id, category, priority, reason, flag
    """

    # Get the complaint description safely
    description = row.get("description", "") or ""
    description_lower = description.lower()

    # ---------------------------------------------------------
    # 1. Severity keywords
    # ---------------------------------------------------------

    severity_keywords = [
        "injury",
        "child",
        "school",
        "hospital",
        "ambulance",
        "fire",
        "hazard",
        "fell",
        "collapse"
    ]

    urgent = False
    severity_keyword = ""

    # Check whether any severity keyword is present
    for i in range(len(severity_keywords)):
        if severity_keywords[i] in description_lower:
            urgent = True
            severity_keyword = severity_keywords[i]
            break

    # Decide priority
    if urgent:
        priority = "Urgent"
    else:
        priority = "Standard"

    # ---------------------------------------------------------
    # 2. Category keywords
    # ---------------------------------------------------------

    category_keywords = {
        "Waste": [
            "waste",
            "garbage",
            "dead animal"
        ],

        "Pothole": [
            "pothole"
        ],

        "Flooding": [
            "flood",
            "flooded",
            "floods"
        ],

        "Drain Blockage": [
            "drain blocked",
            "drain blockage"
        ],

        "Streetlight": [
            "streetlight",
            "streetlights"
        ],

        "Noise": [
            "noise",
            "music"
        ],

        "Heritage Damage": [
            "heritage"
        ],

        "Heat Hazard": [
            "heat"
        ],

        "Road Damage": [
            "road surface",
            "cracked",
            "sinking",
            "footpath"
        ]
    }

    # ---------------------------------------------------------
    # 3. Find matching categories
    # ---------------------------------------------------------

    matches = []

    for category_name, keywords in category_keywords.items():

        for keyword in keywords:

            if keyword in description_lower:
                matches.append((category_name, keyword))
                break

    # ---------------------------------------------------------
    # 4. Decide category, flag and reason
    # ---------------------------------------------------------

    if len(matches) == 1:

        # Exactly one category matched
        category = matches[0][0]
        matched_keyword = matches[0][1]
        flag = ""

        # Include the severity keyword in the reason if urgent
        if urgent:

            reason = (
                f'The complaint description contains '
                f'"{matched_keyword}" and "{severity_keyword}".'
            )

        else:

            reason = (
                f'The complaint description contains '
                f'"{matched_keyword}".'
            )

    elif len(matches) > 1:

        # Multiple categories matched
        # Therefore the complaint is ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"

        matched_categories = []

        for match in matches:
            matched_categories.append(match[0])

        reason = (
            f'The description contains keywords matching multiple '
            f'categories: {", ".join(matched_categories)}.'
        )

    else:

        # No category matched
        category = "Other"
        flag = "NEEDS_REVIEW"

        reason = (
            f'The description does not contain a clear category keyword: '
            f'"{description}".'
        )

    # ---------------------------------------------------------
    # 5. Return the classification result
    # ---------------------------------------------------------

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results CSV.

    Bad rows should not stop the entire process.
    """

    results = []

    # ---------------------------------------------------------
    # 1. Read input CSV
    # ---------------------------------------------------------

    with open(
        input_path,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        # Process every complaint row
        for row in reader:

            try:

                result = classify_complaint(row)
                results.append(result)

            except Exception:

                # If a row causes an error,
                # create a review result instead of crashing.
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": (
                        "The complaint could not be processed reliably."
                    ),
                    "flag": "NEEDS_REVIEW"
                }

                results.append(result)

    # ---------------------------------------------------------
    # 2. Write output CSV
    # ---------------------------------------------------------

    fieldnames = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag"
    ]

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        # Write column names
        writer.writeheader()

        # Write every classification result
        for result in results:
            writer.writerow(result)


# -------------------------------------------------------------
# Program entry point
# -------------------------------------------------------------

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