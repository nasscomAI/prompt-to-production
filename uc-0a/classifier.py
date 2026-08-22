"""
UC-0A — Complaint Classifier
"""

import argparse
import csv


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
    Classify a single complaint row.

    Returns:
        dict with keys:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    # ---------------------------------------------------------
    # Invalid description
    # ---------------------------------------------------------

    if not isinstance(description, str) or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing or invalid.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.strip()
    lower_text = text.lower()

    # ---------------------------------------------------------
    # Priority
    # ---------------------------------------------------------

    priority = "Standard"
    found_severity_keyword = None

    for keyword in SEVERITY_KEYWORDS:
        if keyword in lower_text:
            found_severity_keyword = keyword
            priority = "Urgent"
            break

    # ---------------------------------------------------------
    # Category detection
    # ---------------------------------------------------------

    matches = []

    # ---------------------------------------------------------
    # Pothole
    # ---------------------------------------------------------

    if (
        "pothole" in lower_text
        or "potholes" in lower_text
    ):
        matches.append("Pothole")

    # ---------------------------------------------------------
    # Flooding
    # ---------------------------------------------------------

    if (
        "flooded" in lower_text
        or "flooding" in lower_text
        or "floods" in lower_text
        or "flood" in lower_text
    ):
        matches.append("Flooding")

    # ---------------------------------------------------------
    # Streetlight
    # ---------------------------------------------------------

    if (
        "streetlight" in lower_text
        or "streetlights" in lower_text
        or "street light" in lower_text
        or "street lights" in lower_text
        or "lights out" in lower_text
        or "light out" in lower_text
        or "unlit" in lower_text
        or "dark at night" in lower_text
        or "darkness" in lower_text
    ):
        matches.append("Streetlight")

    # ---------------------------------------------------------
    # Waste
    # ---------------------------------------------------------

    if (
        "garbage" in lower_text
        or "waste" in lower_text
        or "trash" in lower_text
        or "rubbish" in lower_text
        or "dead animal" in lower_text
        or "waste bins" in lower_text
        or "bins overflowing" in lower_text
        or "overflowing garbage" in lower_text
        or "waste overflow" in lower_text
    ):
        matches.append("Waste")

    # ---------------------------------------------------------
    # Noise
    # ---------------------------------------------------------

    if (
        "noise" in lower_text
        or "music" in lower_text
        or "wedding band" in lower_text
        or "band playing" in lower_text
        or "amplifier" in lower_text
        or "amplifiers" in lower_text
        or "drilling" in lower_text
        or "loud" in lower_text
        or "audible" in lower_text
    ):
        matches.append("Noise")

    # ---------------------------------------------------------
    # Heritage Damage
    # ---------------------------------------------------------
    # Heritage context alone is NOT enough.
    # There must be evidence of damage, removal, alteration,
    # defacement, or failure to restore a heritage element.

    if (
        ("heritage" in lower_text or "historic" in lower_text)
        and (
            "damaged" in lower_text
            or "damage" in lower_text
            or "broken" in lower_text
            or "defaced" in lower_text
            or "knocked over" in lower_text
            or "not restored" in lower_text
            or "not replaced" in lower_text
            or "removed" in lower_text
            or "cobblestones broken" in lower_text
            or "heritage stone" in lower_text
            or "heritage lamp" in lower_text
            or "heritage building" in lower_text
        )
    ):
        matches.append("Heritage Damage")

    # ---------------------------------------------------------
    # Heat Hazard
    # ---------------------------------------------------------

    if (
        "heatwave" in lower_text
        or "heat wave" in lower_text
        or "temperature" in lower_text
        or "°c" in lower_text
        or "dangerous temperatures" in lower_text
        or "melting" in lower_text
        or "storing heat" in lower_text
        or "unbearable" in lower_text
        or "heat" in lower_text
    ):
        matches.append("Heat Hazard")

    # ---------------------------------------------------------
    # Drain Blockage
    # ---------------------------------------------------------

    if (
        "drain blocked" in lower_text
        or "drain completely blocked" in lower_text
        or "main drain blocked" in lower_text
        or "drain blockage" in lower_text
        or "blocked drain" in lower_text
        or (
            "drain" in lower_text
            and "blocked" in lower_text
        )
    ):
        matches.append("Drain Blockage")

    # ---------------------------------------------------------
    # Road Damage
    # ---------------------------------------------------------

    if (
        "road surface" in lower_text
        or "road collapsed" in lower_text
        or "road collapse" in lower_text
        or "road subsidence" in lower_text
        or "road subsided" in lower_text
        or "road surface cracked" in lower_text
        or "road surface buckled" in lower_text
        or "road surface bubbling" in lower_text
        or "road sinking" in lower_text
        or "road sank" in lower_text
        or "footpath broken" in lower_text
        or "footpath tiles broken" in lower_text
        or "paving removed" in lower_text
        or (
            "paving" in lower_text
            and "broken" in lower_text
        )
        or (
            "bench" in lower_text
            and "paving" in lower_text
        )
        or "manhole cover missing" in lower_text
        or "road dividers" in lower_text
    ):
        matches.append("Road Damage")

    # Remove duplicate categories
    matches = list(dict.fromkeys(matches))

    # ---------------------------------------------------------
    # Resolve category
    # ---------------------------------------------------------

    category = "Other"
    flag = ""

    if len(matches) == 0:

        category = "Other"
        flag = "NEEDS_REVIEW"

    elif len(matches) == 1:

        category = matches[0]

    else:

        # -----------------------------------------------------
        # Resolve multiple matches.
        #
        # Direct physical damage to a heritage object should
        # take priority over generic road damage.
        # -----------------------------------------------------

        if "Heritage Damage" in matches:
            category = "Heritage Damage"

        elif "Pothole" in matches:
            category = "Pothole"

        elif "Flooding" in matches:
            category = "Flooding"

        elif "Streetlight" in matches:
            category = "Streetlight"

        elif "Drain Blockage" in matches:
            category = "Drain Blockage"

        elif "Waste" in matches:
            category = "Waste"

        elif "Noise" in matches:
            category = "Noise"

        elif "Heat Hazard" in matches:
            category = "Heat Hazard"

        elif "Road Damage" in matches:
            category = "Road Damage"

        else:
            category = "Other"
            flag = "NEEDS_REVIEW"

    # ---------------------------------------------------------
    # Reason
    # ---------------------------------------------------------

    if found_severity_keyword:

        reason = (
            f"The description contains the severity keyword "
            f"'{found_severity_keyword}', so the priority is Urgent."
        )

    elif category != "Other":

        reason = (
            f"The description reports '{text}', "
            f"which supports the {category} category."
        )

    else:

        reason = (
            f"The description reports '{text}', "
            f"but no allowed category is clearly supported."
        )

    # ---------------------------------------------------------
    # Final validation
    # ---------------------------------------------------------

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
    Read input CSV, classify each row, and write results CSV.

    Invalid rows are handled without stopping the complete batch.
    """

    results = []

    try:

        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as infile:

            reader = csv.DictReader(infile)

            if reader.fieldnames is None:
                raise ValueError(
                    "Input CSV has no header."
                )

            required_columns = {
                "complaint_id",
                "description"
            }

            missing_columns = (
                required_columns
                - set(reader.fieldnames)
            )

            if missing_columns:
                raise ValueError(
                    f"Missing required columns: "
                    f"{', '.join(sorted(missing_columns))}"
                )

            for row in reader:

                try:

                    result = classify_complaint(row)
                    results.append(result)

                except Exception as error:

                    results.append(
                        {
                            "complaint_id": row.get(
                                "complaint_id",
                                ""
                            ),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": (
                                "The complaint could not be "
                                "classified because the input "
                                "row was invalid."
                            ),
                            "flag": "NEEDS_REVIEW",
                        }
                    )

                    print(
                        f"Warning: Could not classify complaint "
                        f"{row.get('complaint_id', '')}: {error}"
                    )

    except FileNotFoundError:

        print(
            f"Error: Input file not found: {input_path}"
        )
        return

    except Exception as error:

        print(
            f"Error reading input CSV: {error}"
        )
        return

    # ---------------------------------------------------------
    # Write output CSV
    # ---------------------------------------------------------

    try:

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
                "flag"
            ]

            writer = csv.DictWriter(
                outfile,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(results)

    except Exception as error:

        print(
            f"Error writing output CSV: {error}"
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