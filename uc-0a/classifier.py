
import argparse
import csv


# Exact category names required by the UC-0A README
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


# Exact priority values required by the UC-0A README
ALLOWED_PRIORITIES = [
    "Urgent",
    "Standard",
    "Low",
]


# Severity keywords that must trigger Urgent
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


# Keywords used to identify the allowed categories
CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole",
        "potholes",
    ],

    "Flooding": [
        "flood",
        "flooding",
        "waterlogged",
        "waterlogging",
    ],

    "Streetlight": [
        "streetlight",
        "street light",
        "lamp post",
        "lamp",
        "light pole",
    ],

    "Waste": [
        "garbage",
        "waste",
        "trash",
        "litter",
        "dump",
        "dumping",
        "rubbish",
    ],

    "Noise": [
        "noise",
        "noisy",
        "loud",
        "sound pollution",
    ],

    "Road Damage": [
        "road damage",
        "damaged road",
        "broken road",
        "cracked road",
        "road crack",
        "road is damaged",
    ],

    "Heritage Damage": [
        "heritage",
        "monument",
        "historical building",
        "historic building",
        "historical site",
        "historic site",
    ],

    "Heat Hazard": [
        "heat hazard",
        "extreme heat",
        "heatwave",
        "heat wave",
        "hot weather",
    ],

    "Drain Blockage": [
        "drain blockage",
        "blocked drain",
        "drain is blocked",
        "clogged drain",
        "drain clogged",
        "blocked drainage",
    ],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single citizen complaint.

    Input:
        row: dictionary containing complaint_id and description.

    Output:
        dictionary containing:
        complaint_id, category, priority, reason, flag.
    """

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    # ---------------------------------------------------------
    # Handle missing description
    # ---------------------------------------------------------
    if description is None or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW",
        }

    description = str(description).strip()
    text = description.lower()

    # ---------------------------------------------------------
    # 1. Determine priority
    # ---------------------------------------------------------
    matched_severity = []

    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            matched_severity.append(keyword)

    if matched_severity:
        priority = "Urgent"
        severity_reason = matched_severity[0]
    else:
        priority = "Standard"
        severity_reason = None

    # ---------------------------------------------------------
    # 2. Determine category
    # ---------------------------------------------------------
    category_matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():

        matched_keywords = [
            keyword
            for keyword in keywords
            if keyword in text
        ]

        if matched_keywords:
            category_matches.append(
                (category, matched_keywords[0])
            )

    # ---------------------------------------------------------
    # 3. Handle category ambiguity
    # ---------------------------------------------------------
    if len(category_matches) == 0:

        category = "Other"
        flag = "NEEDS_REVIEW"

        if severity_reason:
            reason = (
                "The description does not provide enough evidence "
                "to determine a specific category, but contains the "
                f"severity keyword '{severity_reason}', requiring "
                "Urgent priority."
            )
        else:
            reason = (
                "The description does not provide enough evidence "
                "to determine a specific category."
            )

    elif len(category_matches) > 1:

        category = "Other"
        flag = "NEEDS_REVIEW"

        matched_categories = [
            match[0]
            for match in category_matches
        ]

        if severity_reason:
            reason = (
                "The description contains evidence for multiple "
                f"categories: {', '.join(matched_categories)}, and "
                f"contains the severity keyword '{severity_reason}', "
                "requiring Urgent priority."
            )
        else:
            reason = (
                "The description contains evidence for multiple "
                f"categories: {', '.join(matched_categories)}."
            )

    else:

        category = category_matches[0][0]
        matched_word = category_matches[0][1]
        flag = ""

        if severity_reason:
            reason = (
                f"The description contains '{matched_word}' indicating "
                f"{category}, and the severity keyword "
                f"'{severity_reason}' requires Urgent priority."
            )
        else:
            reason = (
                f"The description contains '{matched_word}', "
                f"indicating the category {category}."
            )

    # ---------------------------------------------------------
    # 4. Final validation
    # ---------------------------------------------------------
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"
        flag = "NEEDS_REVIEW"

    if flag not in ["", "NEEDS_REVIEW"]:
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
    Read input CSV, classify every complaint,
    and write results to the output CSV.

    Requirements:
    - Do not crash because of a bad individual row.
    - Flag missing or invalid rows.
    - Produce an output row for every input row.
    - Always write the required output columns.
    """

    results = []

    try:

        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as input_file:

            reader = csv.DictReader(input_file)

            # -------------------------------------------------
            # Validate input CSV
            # -------------------------------------------------
            if reader.fieldnames is None:
                raise ValueError(
                    "Input CSV has no header."
                )

            required_columns = {
                "complaint_id",
                "description",
            }

            missing_columns = (
                required_columns - set(reader.fieldnames)
            )

            if missing_columns:
                raise ValueError(
                    "Missing required columns: "
                    + ", ".join(sorted(missing_columns))
                )

            # -------------------------------------------------
            # Process each row independently
            # -------------------------------------------------
            for row_number, row in enumerate(
                reader,
                start=2
            ):

                try:

                    result = classify_complaint(row)
                    results.append(result)

                except Exception as error:

                    # A bad row must not stop the entire batch
                    results.append({
                        "complaint_id": row.get(
                            "complaint_id",
                            f"ROW_{row_number}"
                        ),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": (
                            "The row could not be classified "
                            f"because of an input error: {error}."
                        ),
                        "flag": "NEEDS_REVIEW",
                    })

    except FileNotFoundError:

        print(
            f"Error: Input file not found: {input_path}"
        )
        return

    except Exception as error:

        print(
            f"Error reading input file: {error}"
        )
        return

    # ---------------------------------------------------------
    # Write output CSV
    # ---------------------------------------------------------
    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    try:

        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as output_file:

            writer = csv.DictWriter(
                output_file,
                fieldnames=output_fields
            )

            writer.writeheader()
            writer.writerows(results)

    except Exception as error:

        print(
            f"Error writing output file: {error}"
        )
        return


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

