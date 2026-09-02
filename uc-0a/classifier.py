"""
UC-0A — Complaint Classifier

Classifies citizen complaints using the fixed UC-0A schema.
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
    "accident risk",
    "structural concern",
    "gas leak",
    "darkness",
]


def classify_category(description: str):
    text = description.lower()
    matches = []

    category_keywords = {
        "Pothole": [
            "pothole",
            "pot hole",
        ],
        "Flooding": [
            "flood",
            "flooding",
            "waterlogged",
            "water logging",
            "rainwater",
            "draining directly onto public road",
            "draining onto public road",
        ],
        "Streetlight": [
            "streetlight",
            "street light",
            "street lamp",
            "lamp post",
            "unlit",
            "unlit after",
            "darkness",
            "substation tripped",
        ],
        "Waste": [
            "garbage",
            "waste",
            "trash",
            "litter",
            "dumping",
            "rubbish",
            "dead animal",
        ],
        "Noise": [
            "noise",
            "loud",
            "loudspeaker",
            "sound pollution",
            "music",
            "loud music",
            "late night music",
            "playing music",
            "drilling",
            "engines on",
            "idling with engines",
            "wedding band",
        ],
        "Road Damage": [
            "road damage",
            "damaged road",
            "broken road",
            "cracked road",
            "road crack",
            "road surface cracked",
            "manhole",
            "footpath",
            "upturned paving",
            "surface bubbling",
            "broken bench",
            "broken glass",
            "shelter roof",
            "dead trees",
            "split branches",
            "road collapsed",
            "collapsed road",
            "road surface buckled",
            "road buckled",
            "road subsided",
            "road surface subsided",
        ],
        "Heritage Damage": [
            "heritage",
            "monument",
            "historical building",
            "historic building",
            "heritage lamp post",
            "historic tram",
            "tram road cobblestones",
            "tagore museum",
        ],
        "Heat Hazard": [
            "heat hazard",
            "extreme heat",
            "heatwave",
            "heat wave",
            "dangerous temperatures",
            "temperature",
            "44°c",
            "45°c",
            "52°c",
            "storing heat",
            "burns",
        ],
        "Drain Blockage": [
            "drain blockage",
            "blocked drain",
            "drain blocked",
            "clogged drain",
            "blocked drainage",
            "stormwater drain",
            "100% blocked",
        ],
    }

    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in text:
                matches.append((category, keyword))
                break

    if not matches:
        return "Other", "", True

    if len(matches) > 1:
        categories = {category for category, _ in matches}

        # A pothole remains the primary category when rainwater
        # is filling the pothole.
        if "Pothole" in categories and "Flooding" in categories:
            for category, matched_text in matches:
                if category == "Pothole":
                    return category, matched_text, False

        # Flooding is the primary issue when both
        # flooding and drain blockage are mentioned.
        if "Flooding" in categories and "Drain Blockage" in categories:
            for category, matched_text in matches:
                if category == "Flooding":
                    return category, matched_text, False

        # Waste is the primary issue when actual waste is mentioned,
        # even if the affected area is a heritage area.
        if "Waste" in categories and "Heritage Damage" in categories:
            for category, matched_text in matches:
                if category == "Waste":
                    return category, matched_text, False

        # Heritage Damage is primary when the damaged object itself
        # is a heritage feature or historic infrastructure.
        if "Heritage Damage" in categories and "Streetlight" in categories:
            for category, matched_text in matches:
                if category == "Heritage Damage":
                    return category, matched_text, False

        # Heritage Damage is primary when historic infrastructure
        # is physically damaged.
        if "Heritage Damage" in categories and "Road Damage" in categories:
            for category, matched_text in matches:
                if category == "Heritage Damage":
                    return category, matched_text, False

        # Heat Hazard is the primary issue when high temperature
        # is mentioned together with physical road/surface damage.
        if "Heat Hazard" in categories and "Road Damage" in categories:
            for category, matched_text in matches:
                if category == "Heat Hazard":
                    return category, matched_text, False

        # Noise is primary when a specific noise source is mentioned.
        if "Noise" in categories and "Heritage Damage" in categories:
            for category, matched_text in matches:
                if category == "Noise":
                    return category, matched_text, False

        # Road Damage is primary when a road is physically damaged,
        # even if another hazard is mentioned.
        if "Road Damage" in categories:
            for category, matched_text in matches:
                if category == "Road Damage":
                    return category, matched_text, False

        # Other genuinely ambiguous combinations need review.
        if len(categories) > 1:
            return "Other", matches[0][1], True

    category, matched_text = matches[0]
    return category, matched_text, False


def classify_priority(description: str) -> str:
    text = description.lower()

    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            return "Urgent"

    return "Standard"


def classify_complaint(row: dict) -> dict:
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": (
                "The description is missing, so the complaint "
                "cannot be classified reliably."
            ),
            "flag": "NEEDS_REVIEW",
        }

    category, matched_text, ambiguous = classify_category(description)
    priority = classify_priority(description)

    if ambiguous:
        reason = (
            f'The description "{description}" does not provide enough '
            "unambiguous evidence for one allowed category."
        )

        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": reason,
            "flag": "NEEDS_REVIEW",
        }

    reason = (
        f'The description mentions "{matched_text}", '
        f"which supports the {category} category."
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
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
                raise ValueError("Input CSV has no header row.")

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
                            "Classification failed safely because of "
                            f"invalid row data: {exc}."
                        ),
                        "flag": "NEEDS_REVIEW",
                    }

                results.append(result)

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

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

        for result in results:
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

    batch_classify(
        args.input,
        args.output
    )

    print(
        f"Done. Results written to {args.output}"
    )