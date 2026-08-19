"""
UC-0A — Complaint Classifier

Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import csv


# ============================================================
# UC-0A ENFORCEMENT RULES
# ============================================================

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

ALLOWED_PRIORITIES = {
    "Urgent",
    "Standard",
    "Low",
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


# ============================================================
# SINGLE COMPLAINT CLASSIFICATION
# ============================================================

def classify_complaint(row: dict) -> dict:
    """
    Classify a single citizen complaint.

    Returns:
        {
            "complaint_id": str,
            "category": str,
            "priority": str,
            "reason": str,
            "flag": str
        }
    """

    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # --------------------------------------------------------
    # Handle missing description
    # --------------------------------------------------------

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # --------------------------------------------------------
    # Category classification
    # --------------------------------------------------------

    category = "Other"
    flag = ""

    if "pothole" in text:
        category = "Pothole"

    elif any(
        word in text
        for word in [
            "flooded",
            "flood",
            "flooding",
            "waterlogged",
        ]
    ):
        category = "Flooding"

    elif "streetlight" in text or "street light" in text:
        category = "Streetlight"

    elif any(
        word in text
        for word in [
            "garbage",
            "waste",
            "dead animal",
            "dumped",
        ]
    ):
        category = "Waste"

    elif any(
        word in text
        for word in [
            "music",
            "noise",
            "loud",
        ]
    ):
        category = "Noise"

    elif any(
        word in text
        for word in [
            "cracked",
            "crack",
            "road surface",
            "road damage",
            "footpath",
            "tiles broken",
            "tiles",
            "manhole",
        ]
    ):
        category = "Road Damage"

    elif "heritage" in text:
        category = "Heritage Damage"

    elif any(
        word in text
        for word in [
            "heat",
            "extreme temperature",
            "heatwave",
        ]
    ):
        category = "Heat Hazard"

    elif any(
        word in text
        for word in [
            "drain blocked",
            "drain blockage",
            "blocked drain",
            "drain",
        ]
    ):
        category = "Drain Blockage"

    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # --------------------------------------------------------
    # Ambiguity enforcement
    # --------------------------------------------------------

    # Flooding + blocked drain:
    # both Flooding and Drain Blockage are supported by evidence.
    if "flood" in text and "drain" in text:
        category = "Flooding"
        flag = "NEEDS_REVIEW"

    # Missing manhole cover:
    # category may reasonably overlap with road/drainage issues.
    elif "manhole" in text:
        category = "Road Damage"
        flag = "NEEDS_REVIEW"

    # Heritage street + lights:
    # Heritage Damage and Streetlight are both plausible.
    elif "heritage" in text and (
        "streetlight" in text
        or "street light" in text
        or "lights out" in text
    ):
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"

    # --------------------------------------------------------
    # Priority classification
    # --------------------------------------------------------

    matched_severity = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if keyword in text
    ]

    if matched_severity:
        priority = "Urgent"
    else:
        # The UC-0A README explicitly defines the Urgent
        # triggers but does not provide a separate deterministic
        # rule for Standard versus Low.
        #
        # Therefore Standard is used as the safe default.
        priority = "Standard"

    # --------------------------------------------------------
    # Final schema enforcement
    # --------------------------------------------------------

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    # --------------------------------------------------------
    # Evidence-based reason
    # --------------------------------------------------------

    evidence = description.rstrip(".")

    if matched_severity:
        reason = (
            f"The complaint describes {evidence} and contains "
            f"the severity keyword '{matched_severity[0]}'."
        )
    else:
        reason = f"The complaint describes {evidence}."

    # --------------------------------------------------------
    # Return final result
    # --------------------------------------------------------

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ============================================================
# BATCH CLASSIFICATION
# ============================================================

def batch_classify(input_path: str, output_path: str):
    """
    Read complaint rows from an input CSV, classify every row,
    and write the results to an output CSV.

    Bad rows are flagged rather than stopping the entire batch.
    """

    results = []

    with open(
        input_path,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as infile:

        reader = csv.DictReader(infile)

        for row in reader:

            try:
                result = classify_complaint(row)

            except Exception as exc:
                result = {
                    "complaint_id": (
                        row.get("complaint_id") or ""
                    ).strip(),

                    "category": "Other",

                    "priority": "Standard",

                    "reason": (
                        "The complaint could not be reliably "
                        f"classified because of an input error: {exc}."
                    ),

                    "flag": "NEEDS_REVIEW",
                }

            results.append(result)

    # --------------------------------------------------------
    # Output schema
    # --------------------------------------------------------

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


# ============================================================
# COMMAND-LINE INTERFACE
# ============================================================

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