"""
UC-0A — Complaint Classifier
"""

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


CATEGORY_RULES = {
    "Pothole": [
        "pothole",
        "potholes",
        "road hole",
    ],
    "Flooding": [
        "flooded",
        "flooding",
        "flood",
        "waterlogging",
        "water logging",
        "in water",
        "rain",
        "stranded",
        "inaccessible",
    ],
    "Streetlight": [
        "streetlight",
        "streetlights",
        "street light",
        "street lights",
        "lamp",
        "lights out",
        "light out",
        "light flickering",
        "lights flickering",
        "sparking",
    ],
    "Waste": [
        "garbage",
        "waste",
        "trash",
        "rubbish",
        "dumped",
        "dumping",
        "dead animal",
        "animal not removed",
        "waste bins",
        "garbage bins",
    ],
    "Noise": [
        "noise",
        "noisy",
        "music",
        "loud",
        "loudspeaker",
        "loud speakers",
        "past midnight",
    ],
    "Road Damage": [
        "road surface",
        "road cracked",
        "cracked road",
        "crack",
        "cracked",
        "sinking",
        "damaged road",
        "broken road",
        "footpath",
        "footpath tiles",
        "tiles broken",
        "tiles",
    ],
    "Heritage Damage": [
        "heritage",
        "heritage street",
        "heritage site",
        "heritage building",
        "historic",
        "historical",
        "monument",
    ],
    "Heat Hazard": [
        "heat",
        "heatwave",
        "heat wave",
        "extreme heat",
        "hot weather",
        "very hot",
    ],
    "Drain Blockage": [
        "drain blocked",
        "drain blockage",
        "blocked drain",
        "blocked drainage",
        "drain is blocked",
        "clogged drain",
        "drain clog",
        "manhole",
    ],
}


def contains_phrase(text, phrase):
    pattern = r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)"
    return re.search(pattern, text.lower()) is not None


def find_matches(description):
    """
    Find categories supported by the complaint description.

    Some complaints contain words related to multiple categories.
    We use contextual priority rules below instead of automatically
    marking every multi-keyword complaint as ambiguous.
    """
    matches = {}

    for category, keywords in CATEGORY_RULES.items():
        found = []

        for keyword in keywords:
            if contains_phrase(description, keyword):
                found.append(keyword)

        if found:
            matches[category] = found

    return matches


def find_urgent_keyword(description):
    for keyword in URGENT_KEYWORDS:
        if contains_phrase(description, keyword):
            return keyword

    return None


def evidence_word(description, keyword):
    pattern = r"(?i)(?<!\w)" + re.escape(keyword) + r"(?!\w)"
    match = re.search(pattern, description)

    if match:
        return match.group(0)

    return keyword


def choose_category(description, matches):
    """
    Resolve known contextual combinations before treating a complaint
    as genuinely ambiguous.
    """

    lower = description.lower()

    # Heritage context is more specific than a streetlight reference.
    if "heritage" in lower or "historic" in lower or "historical" in lower:
        if "heritage street" in lower or "heritage site" in lower:
            return "Heritage Damage"

    # A missing manhole is a drainage-infrastructure issue.
    if "manhole" in lower:
        return "Drain Blockage"

    # Flooding is the primary issue when a complaint describes an area
    # becoming flooded, even if a blocked drain is also mentioned.
    if (
        "flood" in lower
        or "flooded" in lower
        or "flooding" in lower
        or "waterlogging" in lower
        or "water logging" in lower
    ):
        return "Flooding"

    # Explicit waste/garbage complaints take priority over generic
    # health-related words.
    if (
        "garbage" in lower
        or "waste" in lower
        or "dead animal" in lower
        or "dumped" in lower
    ):
        return "Waste"

    # Noise complaints should use the Noise category even when
    # they contain timing/context words such as midnight.
    if (
        "music" in lower
        or "noise" in lower
        or "loud" in lower
    ):
        return "Noise"

    # Streetlight complaints should be classified as Streetlight
    # unless a more specific heritage context was detected above.
    if (
        "streetlight" in lower
        or "street light" in lower
        or "lights out" in lower
        or "light flickering" in lower
    ):
        return "Streetlight"

    # Footpath damage belongs to Road Damage in the allowed taxonomy.
    if "footpath" in lower or "tiles" in lower:
        return "Road Damage"

    if len(matches) == 1:
        return next(iter(matches))

    if not matches:
        return "Other"

    # If multiple categories remain and no contextual rule resolves them,
    # the complaint is genuinely ambiguous.
    return None


def classify_complaint(row):
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "")

    urgent_keyword = find_urgent_keyword(description)

    if urgent_keyword:
        priority = "Urgent"
    else:
        priority = "Standard"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": "The description is empty, so no specific complaint category can be identified.",
            "flag": "NEEDS_REVIEW",
        }

    matches = find_matches(description)
    category = choose_category(description, matches)

    if category is None:
        evidence = "; ".join(
            f'{cat}: "{evidence_word(description, words[0])}"'
            for cat, words in matches.items()
        )

        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": (
                "The description contains conflicting category evidence: "
                f"{evidence}."
            ),
            "flag": "NEEDS_REVIEW",
        }

    if category == "Other":
        words = re.findall(r"\b[A-Za-z]+\b", description)
        evidence = " ".join(words[:10])

        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": (
                f'No allowed category clearly matches the description words "{evidence}".'
            ),
            "flag": "NEEDS_REVIEW",
        }

    # Use a category-specific matched phrase in the reason.
    matched_words = matches.get(category, [])

    if matched_words:
        evidence = evidence_word(description, matched_words[0])
    else:
        # Contextual classifications such as Heritage Damage.
        if category == "Heritage Damage":
            evidence = "heritage"
        elif category == "Drain Blockage":
            evidence = "manhole"
        elif category == "Flooding":
            evidence = "flooded"
        elif category == "Waste":
            evidence = "waste"
        elif category == "Noise":
            evidence = "music"
        elif category == "Streetlight":
            evidence = "streetlights"
        elif category == "Road Damage":
            evidence = "footpath"
        else:
            evidence = category

    reason = (
        f'Classified as {category} because the description contains "{evidence}".'
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path, output_path):
    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    results = []

    with open(
        input_path,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as infile:

        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")

        required_fields = {"complaint_id", "description"}
        missing = required_fields - set(reader.fieldnames)

        if missing:
            raise ValueError(
                "Input CSV is missing required field(s): "
                + ", ".join(sorted(missing))
            )

        for row in reader:
            results.append(classify_complaint(row))

    with open(
        output_path,
        mode="w",
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