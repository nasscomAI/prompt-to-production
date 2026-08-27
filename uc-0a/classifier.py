import argparse
import csv
import re


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

URGENT_KEYWORDS = [
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


def contains_keyword(text, keyword):
    """Match a keyword as a complete word or phrase."""
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return re.search(pattern, text, re.IGNORECASE) is not None


def find_category(description):
    """Determine the most appropriate complaint category."""

    text = description.lower()

    category_rules = {
        "Pothole": [
            "pothole",
            "pot hole",
        ],

        "Flooding": [
            "flood",
            "flooded",
            "flooding",
            "waterlogged",
            "water logging",
            "waterlogging",
            "underpass flooded",
            "bridge approach floods",
        ],

        "Streetlight": [
            "streetlight",
            "streetlights",
            "street light"
            "lamp post",
            "lights out",
            "light out",
            "light not working",
            "sparking",
            "flickering",
        ],

        "Waste": [
            "garbage",
            "waste",
            "trash",
            "litter",
            "rubbish",
            "dumped",
            "dump",
            "dead animal",
            "animal not removed",
        ],

        "Noise": [
            "noise",
            "noisy",
            "loud",
            "music past midnight",
            "music",
            "sound pollution",
        ],

        "Road Damage": [
            "road damage",
            "damaged road",
            "broken road",
            "cracked road",
            "road crack",
            "road surface cracked",
            "road surface",
            "sinking",
            "footpath tiles broken",
            "footpath",
            "broken tiles",
        ],

        "Heritage Damage": [
            "heritage",
            "monument",
            "historical building",
            "historic building",
        ],

        "Heat Hazard": [
            "heat",
            "extreme heat",
            "heat hazard",
            "hot surface",
        ],

        "Drain Blockage": [
            "drain",
            "blocked drain",
            "drain blockage",
            "clogged drain",
            "blocked drainage",
            "drainage blockage",
        ],
    }

    matches = []

    for category, keywords in category_rules.items():
        matched = [
            keyword
            for keyword in keywords
            if contains_keyword(text, keyword)
        ]

        if matched:
            matches.append((category, matched))

    # No reliable category
    if not matches:
        return "Other", [], True

    # More than one category requires review.
    # Flooding + drain blockage is especially relevant because both
    # are explicitly present in the complaint.
    if len(matches) > 1:
        return "Other", matches, True

    category, matched_words = matches[0]
    return category, matched_words, False


def find_urgent_keyword(description):
    """Return the first explicit urgent severity keyword found."""

    text = description.lower()

    for keyword in URGENT_KEYWORDS:
        if contains_keyword(text, keyword):
            return keyword

    return None


def classify_complaint(row):
    complaint_id = row.get("complaint_id", "")

    description = (
        row.get("description")
        or row.get("complaint")
        or row.get("complaint_description")
        or row.get("text")
        or ""
    ).strip()

    # Missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    category, matches, ambiguous = find_category(description)

    urgent_keyword = find_urgent_keyword(description)

    if urgent_keyword:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Ambiguous category
    if ambiguous:
        if matches:
            categories = ", ".join(match[0] for match in matches)
            reason = (
                f"The description contains terms matching multiple categories: "
                f"{categories}."
            )
        else:
            reason = (
                "The description does not clearly match an allowed category."
            )

        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": reason,
            "flag": "NEEDS_REVIEW",
        }

    matched_word = matches[0]

    if urgent_keyword:
        reason = (
            f"The description contains '{matched_word}' and the severity "
            f"keyword '{urgent_keyword}', so the complaint is urgent."
        )
    else:
        reason = (
            f"The description contains '{matched_word}' and matches "
            f"the {category} category."
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path, output_path):
    results = []

    with open(
        input_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as infile:

        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "The complaint could not be classified reliably.",
                    "flag": "NEEDS_REVIEW",
                }

            results.append(result)

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
        encoding="utf-8",
        newline=""
    ) as outfile:

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
        help="Input CSV file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV file"
    )

    args = parser.parse_args()

    batch_classify(
        args.input,
        args.output
    )

    print(
        f"Done. Results written to {args.output}"
    )