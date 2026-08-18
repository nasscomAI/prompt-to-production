import argparse
import csv


SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "children",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse"
]


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row."""

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No complaint description was provided.",
            "flag": "NEEDS_REVIEW"
        }

    text = description.lower()

    category = "Other"
    flag = ""

    # Category classification
    if "pothole" in text:
        category = "Pothole"

    elif any(word in text for word in [
        "flood", "flooded", "flooding",
        "waterlogged", "water logging"
    ]):
        category = "Flooding"

    elif any(word in text for word in [
        "streetlight", "street light",
        "streetlights", "lights out",
        "light not working", "flickering"
    ]):
        category = "Streetlight"

    elif any(word in text for word in [
        "garbage", "waste", "trash",
        "dumped", "dump", "dead animal"
    ]):
        category = "Waste"

    elif any(word in text for word in [
        "noise", "loud", "music",
        "noisy", "sound"
    ]):
        category = "Noise"

    elif any(word in text for word in [
        "road surface", "road damaged",
        "damaged road", "cracked",
        "sinking", "footpath",
        "tiles broken"
    ]):
        category = "Road Damage"

    elif any(word in text for word in [
        "heritage", "monument",
        "historic", "heritage street"
    ]):
        category = "Heritage Damage"

    elif any(word in text for word in [
        "heat", "heatwave",
        "heat wave", "extreme hot"
    ]):
        category = "Heat Hazard"

    elif any(word in text for word in [
        "drain blocked", "blocked drain",
        "drainage blocked", "blocked gutter",
        "clogged drain"
    ]):
        category = "Drain Blockage"

    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority classification
    priority = "Standard"

    if any(keyword in text for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"

    # Evidence words for the reason
    evidence = {
        "Pothole": ["pothole"],
        "Flooding": ["flooded", "floods", "flood", "water"],
        "Streetlight": [
            "streetlight",
            "streetlights",
            "lights out",
            "flickering"
        ],
        "Waste": [
            "garbage",
            "waste",
            "dumped",
            "dead animal"
        ],
        "Noise": [
            "music",
            "noise",
            "loud",
            "sound"
        ],
        "Road Damage": [
            "cracked",
            "sinking",
            "footpath",
            "broken",
            "upturned"
        ],
        "Heritage Damage": [
            "heritage",
            "monument",
            "historic"
        ],
        "Heat Hazard": [
            "heat",
            "heatwave",
            "heat wave"
        ],
        "Drain Blockage": [
            "drain blocked",
            "blocked drain",
            "clogged"
        ]
    }

    matched_word = ""

    for word in evidence.get(category, []):
        if word in text:
            matched_word = word
            break

    if category == "Other":
        reason = (
            "Classified as Other because the complaint does not clearly "
            "match an allowed category."
        )
    else:
        reason = (
            f'Classified as {category} based on the words '
            f'"{matched_word}" in the description.'
        )

    # This return block was missing
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify rows, and write results."""

    fieldnames = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag"
    ]

    with open(
        input_path,
        "r",
        newline="",
        encoding="utf-8"
    ) as input_file, open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as output_file:

        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(
            output_file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get(
                        "complaint_id", ""
                    ),
                    "category": "Other",
                    "priority": "Low",
                    "reason": (
                        "The complaint could not be processed."
                    ),
                    "flag": "NEEDS_REVIEW"
                }

            writer.writerow(result)


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