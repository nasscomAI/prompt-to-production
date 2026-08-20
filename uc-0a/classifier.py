"""
UC-0A Complaint Classifier
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

ALLOWED_PRIORITIES = {
    "Urgent",
    "Standard",
    "Low",
}

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
    complaint_id = str(row.get("complaint_id", "") or "").strip()
    description = str(row.get("description", "") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is missing, so the complaint cannot be classified.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Priority
    priority = "Urgent" if any(
        keyword in text for keyword in SEVERITY_KEYWORDS
    ) else "Standard"

    # Category
    category = None

    if "pothole" in text:
        category = "Pothole"

    elif any(
        phrase in text
        for phrase in (
            "drain blocked",
            "drain blockage",
            "blocked drain",
            "drain clogged",
            "clogged drain",
        )
    ):
        category = "Drain Blockage"

    elif any(
        phrase in text
        for phrase in (
            "flood",
            "flooded",
            "flooding",
            "waterlogged",
            "water logging",
            "standing water",
        )
    ):
        category = "Flooding"

    elif any(
        phrase in text
        for phrase in (
            "streetlight",
            "street light",
            "streetlights",
            "street lights",
            "lights out",
            "light out",
            "light flickering",
            "lighting",
        )
    ):
        category = "Streetlight"

    elif any(
        phrase in text
        for phrase in (
            "garbage",
            "waste",
            "rubbish",
            "dumped",
            "dead animal",
            "animal not removed",
        )
    ):
        category = "Waste"

    elif any(
        phrase in text
        for phrase in (
            "music",
            "noise",
            "loud",
            "sound",
        )
    ):
        category = "Noise"

    elif any(
        phrase in text
        for phrase in (
            "cracked",
            "crack",
            "sinking",
            "broken road",
            "road surface",
            "footpath",
            "manhole",
            "bridge approach",
            "road damage",
        )
    ):
        category = "Road Damage"

    elif any(
        phrase in text
        for phrase in (
            "heritage",
            "historic",
            "historical",
        )
    ):
        category = "Heritage Damage"

    elif any(
        phrase in text
        for phrase in (
            "heat",
            "heatwave",
            "heat wave",
            "extreme temperature",
        )
    ):
        category = "Heat Hazard"

    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    reason = (
        f'The description states "{description}", '
        f"indicating {category.lower()}."
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(
        input_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as infile:

        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")

        for row in reader:
            try:
                result = classify_complaint(row)

                if result["category"] not in ALLOWED_CATEGORIES:
                    result["category"] = "Other"
                    result["flag"] = "NEEDS_REVIEW"

                if result["priority"] not in ALLOWED_PRIORITIES:
                    result["priority"] = "Standard"
                    result["flag"] = "NEEDS_REVIEW"

                results.append(result)

            except Exception as exc:
                complaint_id = str(
                    row.get("complaint_id", "") or ""
                ).strip()

                results.append({
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed: {exc}.",
                    "flag": "NEEDS_REVIEW",
                })

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
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

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")