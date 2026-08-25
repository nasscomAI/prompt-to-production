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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

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


CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole",
        "pit",
        "pits",
    ],
    "Flooding": [
        "flood",
        "flooded",
        "flooding",
        "waterlogged",
        "water logging",
        "waterlogging",
        "inaccessible",
    ],
    "Streetlight": [
        "streetlight",
        "street light",
        "streetlights",
        "lights out",
        "light out",
        "lamp",
        "light pole",
        "lights are not working",
        "flickering",
        "sparking",
    ],
    "Waste": [
        "garbage",
        "waste",
        "trash",
        "litter",
        "rubbish",
        "dump",
        "dumped",
        "bins",
    ],
    "Noise": [
        "noise",
        "loud",
        "loudspeaker",
        "sound pollution",
        "music",
        "playing music",
    ],
    "Road Damage": [
        "road damage",
        "damaged road",
        "broken road",
        "cracked road",
        "road is broken",
        "road is damaged",
        "road surface cracked",
        "road surface",
        "sinking",
        "footpath tiles",
        "footpath",
        "broken tiles",
    ],
    "Heritage Damage": [
        "heritage damage",
        "heritage building",
        "monument damage",
        "historical damage",
        "historic building",
    ],
    "Heat Hazard": [
        "heat",
        "extreme heat",
        "heatwave",
        "heat wave",
    ],
    "Drain Blockage": [
        "drain",
        "drainage",
        "blocked drain",
        "drain blockage",
        "sewer",
    ],
}



def classify_complaint(row: dict) -> dict:
    """
    Classify one complaint row.

    Returns:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "")
    description = str(
        row.get("description", row.get("complaint", ""))
        or ""
    ).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No complaint description was provided.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Priority rule
    matched_severity = next(
        (word for word in SEVERITY_KEYWORDS if word in text),
        None
    )

    priority = "Urgent" if matched_severity else "Standard"

    # Find category matches
    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                matches.append((category, keyword))
                break

    # Ambiguous or unknown category
    if len(matches) == 0:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f'The description contains no specific category keyword: "{description}".',
            "flag": "NEEDS_REVIEW",
        }

    if len(matches) > 1:
        matched_words = ", ".join(f'"{word}"' for _, word in matches)
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f"The description contains multiple possible category indicators: {matched_words}.",
            "flag": "NEEDS_REVIEW",
        }

    category, matched_keyword = matches[0]

    reason = (
        f'The complaint mentions "{matched_keyword}", '
        f'which indicates {category}.'
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify every row, and write results CSV.
    Bad rows should not stop the complete batch.
    """

    results = []

    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError("Input CSV has no header.")

            for row_number, row in enumerate(reader, start=2):

                try:
                    if not row:
                        continue

                    result = classify_complaint(row)

                    # Preserve original fields
                    output_row = dict(row)

                    # Add required classification fields
                    output_row.update(result)

                    results.append(output_row)

                except Exception as exc:
                    # Do not crash on one bad row
                    results.append({
                        "complaint_id": row.get("complaint_id", f"row-{row_number}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row could not be classified because of an input error: {str(exc)}.",
                        "flag": "NEEDS_REVIEW",
                    })

    except Exception as exc:
        print(f"Could not read input file: {exc}")
        return

    # Always try to produce an output file
    fieldnames = []

    if results:
        for row in results:
            for key in row.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

    # Ensure required fields exist
    for field in ["complaint_id", "category", "priority", "reason", "flag"]:
        if field not in fieldnames:
            fieldnames.append(field)

    try:
        with open(output_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                extrasaction="ignore"
            )

            writer.writeheader()
            writer.writerows(results)

    except Exception as exc:
        print(f"Could not write output file: {exc}")


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

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")