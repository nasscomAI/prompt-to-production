"""
UC-0A Complaint Classifier
"""

import argparse
import csv


URGENT_KEYWORDS = [
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

CATEGORY_RULES = {
    "Pothole": [
        "pothole"
    ],

    "Flooding": [
        "flood",
        "flooding",
        "waterlogged",
        "water logging"
    ],

    "Streetlight": [
        "streetlight",
        "street light",
        "unlit",
        "dark",
        "lighting",
        "wiring theft"
    ],

    "Waste": [
        "waste",
        "garbage",
        "trash",
        "bins",
        "overflowing"
    ],

    "Noise": [
        "noise",
        "music",
        "audible",
        "loud"
    ],

    "Road Damage": [
        "road damage",
        "road surface",
        "subsidence",
        "lane closure",
        "paving"
    ],

    "Heritage Damage": [
        "heritage",
        "step well",
        "historic",
        "monument"
    ],

    "Heat Hazard": [
        "heat",
        "44°c",
        "45°c",
        "52°c",
        "temperature",
        "melting",
        "burns",
        "unsafe",
        "sun"
    ],

    "Drain Blockage": [
        "drain",
        "drainage",
        "blocked drain",
        "clogged drain"
    ]
}


def classify_complaint(row):
    description = str(row.get("description", "")).strip()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing.",
            "flag": "NEEDS_REVIEW"
        }

    text = description.lower()

    category = None

    for cat, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            category = cat
            break

    flag = ""

    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"

    priority = "Standard"

    if any(keyword in text for keyword in URGENT_KEYWORDS):
        priority = "Urgent"

    reason = (
        f"Classified as {category} based on complaint text: "
        f"'{description[:75]}'."
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path, output_path):
    output_rows = []

    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as ex:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification error: {str(ex)}",
                    "flag": "NEEDS_REVIEW"
                }

            output_rows.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag"
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV"
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")