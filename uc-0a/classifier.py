"""
UC-0A — Complaint Classifier

Implements the UC-0A RICE/CRAFT enforcement rules:
- Exact category taxonomy
- Severity-based priority
- Evidence-based reason
- NEEDS_REVIEW for ambiguity
- Robust batch processing
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


def classify_category(description: str) -> tuple[str, bool]:
    """
    Determine the complaint category using only the description.

    Returns:
        (category, needs_review)
    """

    text = description.lower()

    matches = []

    # Pothole
    if any(word in text for word in [
        "pothole",
        "potholes",
    ]):
        matches.append("Pothole")

    # Flooding
    if any(word in text for word in [
        "flood",
        "flooding",
        "waterlogged",
        "water logging",
        "waterlogging",
    ]):
        matches.append("Flooding")

    # Streetlight
    if any(word in text for word in [
        "streetlight",
        "street light",
        "street lamp",
        "lamp post",
        "lamp",
        "light not working",
        "lights not working",
    ]):
        matches.append("Streetlight")

    # Waste
    if any(word in text for word in [
        "garbage",
        "waste",
        "trash",
        "rubbish",
        "litter",
        "dump",
        "dumping",
        "uncleared garbage",
    ]):
        matches.append("Waste")

    # Noise
    if any(word in text for word in [
        "noise",
        "noisy",
        "loud music",
        "loudspeaker",
        "loud speaker",
        "sound pollution",
    ]):
        matches.append("Noise")

    # Road Damage
    if any(word in text for word in [
        "road damage",
        "damaged road",
        "broken road",
        "road broken",
        "cracked road",
        "crack in road",
        "road crack",
    ]):
        matches.append("Road Damage")

    # Heritage Damage
    if any(word in text for word in [
        "heritage",
        "monument",
        "historical building",
        "historic building",
        "historic site",
        "historical site",
    ]):
        matches.append("Heritage Damage")

    # Heat Hazard
    if any(word in text for word in [
        "heat hazard",
        "extreme heat",
        "heatwave",
        "heat wave",
        "heat hazard",
    ]):
        matches.append("Heat Hazard")

    # Drain Blockage
    if any(word in text for word in [
        "drain blocked",
        "blocked drain",
        "drain blockage",
        "drain is blocked",
        "clogged drain",
        "drain clog",
        "drain overflowing",
    ]):
        matches.append("Drain Blockage")

    # No category evidence
    if not matches:
        return "Other", True

    # More than one possible category = ambiguity
    unique_matches = list(dict.fromkeys(matches))

    if len(unique_matches) > 1:
        return "Other", True

    category = unique_matches[0]

    if category not in ALLOWED_CATEGORIES:
        return "Other", True

    return category, False


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns:
        complaint_id
        category
        priority
        reason
        flag
    """

    complaint_id = str(
        row.get("complaint_id")
        or row.get("id")
        or ""
    ).strip()

    description = str(
        row.get("description")
        or row.get("complaint")
        or row.get("text")
        or ""
    ).strip()

    # Handle missing/null descriptions safely.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The description is missing, so the complaint cannot be classified.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # UC-0A rule:
    # Any severity keyword makes priority Urgent.
    found_severity = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if keyword in text
    ]

    if found_severity:
        priority = "Urgent"
    else:
        priority = "Standard"

    category, needs_review = classify_category(description)

    # Build a reason using actual words from the description.
    if needs_review:
        if found_severity:
            reason = (
                f'The description contains "{found_severity[0]}" but the '
                f'category is ambiguous from the description.'
            )
        else:
            reason = (
                "The description does not provide enough specific information "
                "to determine one allowed category."
            )
        flag = "NEEDS_REVIEW"
    else:
        # Find a useful category keyword actually appearing in the description.
        category_evidence = {
            "Pothole": ["pothole", "potholes"],
            "Flooding": ["flood", "flooding", "waterlogged", "waterlogging"],
            "Streetlight": [
                "streetlight",
                "street light",
                "street lamp",
                "lamp post",
            ],
            "Waste": [
                "garbage",
                "waste",
                "trash",
                "rubbish",
                "litter",
                "dump",
            ],
            "Noise": [
                "noise",
                "noisy",
                "loud music",
                "loudspeaker",
            ],
            "Road Damage": [
                "road damage",
                "damaged road",
                "broken road",
                "cracked road",
            ],
            "Heritage Damage": [
                "heritage",
                "monument",
                "historical building",
                "historic building",
            ],
            "Heat Hazard": [
                "heat hazard",
                "extreme heat",
                "heatwave",
                "heat wave",
            ],
            "Drain Blockage": [
                "drain blocked",
                "blocked drain",
                "drain blockage",
                "clogged drain",
            ],
        }

        evidence = None

        for keyword in category_evidence.get(category, []):
            if keyword in text:
                evidence = keyword
                break

        if evidence:
            reason = f'The description mentions "{evidence}", indicating {category}.'
        else:
            reason = f"The description supports the {category} category."

        flag = ""

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

    Bad rows do not stop the complete batch.
    """

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    results = []

    try:
        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as infile:

            reader = csv.DictReader(infile)

            if reader.fieldnames is None:
                raise ValueError("Input CSV has no header row.")

            for row_number, row in enumerate(reader, start=2):
                try:
                    if not row:
                        results.append({
                            "complaint_id": f"row-{row_number}",
                            "category": "Other",
                            "priority": "Low",
                            "reason": "The row is empty and cannot be classified.",
                            "flag": "NEEDS_REVIEW",
                        })
                        continue

                    result = classify_complaint(row)
                    results.append(result)

                except Exception as exc:
                    # Do not crash the entire batch.
                    results.append({
                        "complaint_id": str(
                            row.get("complaint_id")
                            or row.get("id")
                            or f"row-{row_number}"
                        ),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Row could not be classified because of an error: {exc}.",
                        "flag": "NEEDS_REVIEW",
                    })

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Could not read input CSV: {exc}"
        )

    # Always write the output file when possible.
    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=output_fields,
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

    print(f"Done. Results written to {args.output}")