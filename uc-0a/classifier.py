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
    "Other"
]


SEVERITY_KEYWORDS = [
    "injury",
    "injured",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse"
]


CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],

    "Flooding": [
        "flood",
        "flooding",
        "flooded",
        "waterlogging",
        "water logged"
    ],

    "Streetlight": [
        "streetlight",
        "street light",
        "lamp post",
        "unlit",
        "lighting"
    ],

    "Waste": [
        "waste",
        "garbage",
        "trash",
        "rubbish",
        "overflowing bins",
        "waste bins"
    ],

    "Noise": [
        "noise",
        "noisy",
        "loud",
        "music",
        "audible"
    ],

    "Road Damage": [
        "road damage",
        "damaged road",
        "cracked road",
        "road surface",
        "road subsidence",
        "paving",
        "pavement",
        "upturned paving"
    ],

    "Heritage Damage": [
        "heritage",
        "historic",
        "ancient",
        "monument",
        "heritage area",
        "old city"
    ],

    "Heat Hazard": [
        "heat",
        "heatwave",
        "heat wave",
        "temperature",
        "temperatures",
        "°c",
        "melting",
        "unbearable",
        "storing heat",
        "dangerous temperatures",
        "burns",
        "full sun",
        "surface bubbling"
    ],

    "Drain Blockage": [
        "drain",
        "blocked drain",
        "drainage",
        "clogged drain"
    ]
}


def classify_complaint(row: dict) -> dict:

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    if not isinstance(description, str) or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is missing or invalid.",
            "flag": "NEEDS_REVIEW"
        }

    text = description.lower()

    # Priority
    priority = "Standard"

    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            priority = "Urgent"
            break

    # Specific category rules
    if "waste" in text or "garbage" in text or "trash" in text:
        return {
            "complaint_id": complaint_id,
            "category": "Waste",
            "priority": priority,
            "reason": 'The description mentions "waste", which indicates Waste.',
            "flag": ""
        }

    if "heritage concern" in text:
        return {
            "complaint_id": complaint_id,
            "category": "Heritage Damage",
            "priority": priority,
            "reason": 'The description mentions "heritage concern", which indicates Heritage Damage.',
            "flag": ""
        }

    # Find category matches
    matched_categories = []

    for category, keywords in CATEGORY_KEYWORDS.items():

        matched_words = []

        for keyword in keywords:
            if keyword in text:
                matched_words.append(keyword)

        if matched_words:
            matched_categories.append(
                (category, matched_words)
            )

    # Heat Hazard takes priority when heat signals exist
    for category, words in matched_categories:

        if category == "Heat Hazard":

            return {
                "complaint_id": complaint_id,
                "category": "Heat Hazard",
                "priority": priority,
                "reason": (
                    f'The description mentions "{words[0]}", '
                    f'which indicates Heat Hazard.'
                ),
                "flag": ""
            }

    # One clear category
    if len(matched_categories) == 1:

        category = matched_categories[0][0]
        word = matched_categories[0][1][0]

        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": (
                f'The description mentions "{word}", '
                f'which indicates {category}.'
            ),
            "flag": ""
        }

    # Multiple or ambiguous categories
    if len(matched_categories) > 1:

        words = []

        for category, matched_words in matched_categories:
            words.extend(matched_words)

        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": (
                f'The description contains multiple category signals: '
                f'"{", ".join(words)}".'
            ),
            "flag": "NEEDS_REVIEW"
        }

    # No category
    return {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": priority,
        "reason": (
            f'The description does not clearly match a defined category: '
            f'"{description.strip()}".'
        ),
        "flag": "NEEDS_REVIEW"
    }


def batch_classify(input_path: str, output_path: str):

    results = []

    try:

        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                try:
                    results.append(
                        classify_complaint(row)
                    )

                except Exception as error:

                    results.append({
                        "complaint_id": row.get(
                            "complaint_id",
                            ""
                        ),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification error: {error}",
                        "flag": "NEEDS_REVIEW"
                    })

    except FileNotFoundError:

        print(f"Input file not found: {input_path}")
        return

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

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier"
    )

    parser.add_argument(
        "--input",
        required=True
    )

    parser.add_argument(
        "--output",
        required=True
    )

    args = parser.parse_args()

    batch_classify(
        args.input,
        args.output
    )

    print(
        f"Done. Results written to {args.output}"
    )