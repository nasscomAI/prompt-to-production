"""
UC-0A — Complaint Classifier
"""
import argparse
import csv


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
    complaint_id = row.get("complaint_id", "")

    description = str(
        row.get("description")
        or row.get("complaint")
        or row.get("text")
        or ""
    ).strip()

    # Handle missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No complaint description was provided.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # -----------------------------
    # PRIORITY
    # -----------------------------
    matched_keywords = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if keyword in text
    ]

    priority = "Urgent" if matched_keywords else "Standard"

    # -----------------------------
    # CATEGORY
    # -----------------------------
    category = "Other"

    if "pothole" in text:
        category = "Pothole"

    elif "flood" in text:
        category = "Flooding"

    elif "streetlight" in text or "street light" in text:
        category = "Streetlight"

    elif (
        "waste" in text
        or "garbage" in text
        or "trash" in text
        or "bulk waste" in text
    ):
        category = "Waste"

    elif (
        "noise" in text
        or "music" in text
        or "loud" in text
        or "playing music" in text
    ):
        category = "Noise"

    elif (
        "road damage" in text
        or "damaged road" in text
        or "road surface" in text
        or "road cracked" in text
        or "road crack" in text
        or "road sinking" in text
        or "cracked and sinking" in text
    ):
        category = "Road Damage"

    elif "heritage" in text:
        category = "Heritage Damage"

    elif "heat" in text:
        category = "Heat Hazard"

    elif "drain" in text and (
        "block" in text
        or "blocked" in text
    ):
        category = "Drain Blockage"

    # -----------------------------
    # FLAG
    # -----------------------------
    flag = ""

    if category == "Other":
        flag = "NEEDS_REVIEW"

    # -----------------------------
    # REASON
    # -----------------------------
    if matched_keywords:
        keyword = matched_keywords[0]

        reason = (
            f"Priority is Urgent because the description contains "
            f"the severity keyword '{keyword}': {description}"
        )
    else:
        reason = (
            f"Category '{category}' is based on the description: "
            f"{description}"
        )

    # Final taxonomy enforcement
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
                    results.append(
                        classify_complaint(row)
                    )

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
        # Still create an output file if input cannot be read
        results.append({
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": f"Input could not be read: {exc}",
            "flag": "NEEDS_REVIEW",
        })

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as outfile:

        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag",
        ]

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