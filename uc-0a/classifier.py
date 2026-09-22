"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re


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


CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole",
        "potholes",
    ],
    "Flooding": [
        "flood",
        "floods",
        "flooded",
        "flooding",
        "waterlogging",
        "water logged",
        "waterlogged",
        "standing water",
        "inaccessible",
    ],
    "Streetlight": [
        "streetlight",
        "streetlights",
        "street lights",
        "lamp post",
        "lamp",
        "lighting",
        "lights out",
        "light out",
        "light not working",
        "lights not working",
    ],
    "Waste": [
        "waste",
        "garbage",
        "trash",
        "rubbish",
        "litter",
        "dumping",
        "dead animal",
    ],
    "Noise": [
        "noise",
        "noisy",
        "music",
        "loud",
        "loudspeaker",
        "sound pollution",
    ],
    "Road Damage": [
        "road damage",
        "damaged road",
        "cracked road",
        "road crack",
        "road surface",
        "road broken",
        "broken road",
        "footpath",
        "footpath tiles",
        "pavement",
        "pavement tiles",
        "upturned tiles",
    ],
    "Heritage Damage": [
        "heritage",
        "heritage damage",
        "heritage site",
        "heritage structure",
        "monument damage",
        "historic damage",
        "historical damage",
    ],
    "Heat Hazard": [
        "heat",
        "heatwave",
        "heat wave",
        "extreme temperature",
        "hot weather",
    ],
    "Drain Blockage": [
        "drain blocked",
        "blocked drain",
        "drain blockage",
        "drain clogged",
        "clogged drain",
        "blocked drainage",
        "drainage blocked",
    ],
}


def contains_keyword(text, keyword):
    """
    Match a keyword case-insensitively.
    Supports phrases containing spaces.
    """
    return re.search(r"\b" + re.escape(keyword) + r"\b", text) is not None


def classify_complaint(row):
    description = row.get("description", "").strip()

    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is missing, so the complaint cannot be categorized reliably.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # -------------------------
    # Priority
    # -------------------------
    matched_severity = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if contains_keyword(text, keyword)
    ]

    priority = "Urgent" if matched_severity else "Standard"

    # -------------------------
    # Category matching
    # -------------------------
    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        found = [
            keyword
            for keyword in keywords
            if contains_keyword(text, keyword)
        ]

        if found:
            matches.append((category, found))

    # No category match
    if not matches:
        return {
            "category": "Other",
            "priority": priority,
            "reason": (
                "The description does not contain a specific category "
                "keyword from the allowed classification schema."
            ),
            "flag": "NEEDS_REVIEW",
        }

    # -------------------------
    # One category match
    # -------------------------
    if len(matches) == 1:
        category, evidence = matches[0]

        return {
            "category": category,
            "priority": priority,
            "reason": (
                f'The description mentions "{evidence[0]}", '
                f"which supports the {category} category."
            ),
            "flag": "",
        }

    # -------------------------
    # Multiple categories
    # -------------------------
    categories = [category for category, _ in matches]

    # Heritage + lighting is genuinely ambiguous.
    if "Heritage Damage" in categories and "Streetlight" in categories:
        evidence = []

        for _, keywords in matches:
            evidence.append(keywords[0])

        return {
            "category": "Other",
            "priority": priority,
            "reason": (
                "The description contains multiple category signals "
                f"({', '.join(evidence)}), so the category needs review."
            ),
            "flag": "NEEDS_REVIEW",
        }

    # Drain blockage + flooding:
    # flooding is the broader reported problem, but preserve the
    # ambiguity rather than silently dropping the second signal.
    if "Flooding" in categories and "Drain Blockage" in categories:
        evidence = []

        for _, keywords in matches:
            evidence.append(keywords[0])

        return {
            "category": "Flooding",
            "priority": priority,
            "reason": (
                "The description contains flooding and drainage signals "
                f"({', '.join(evidence)}), so the flooding category is "
                "selected while the related drainage condition is preserved."
            ),
            "flag": "NEEDS_REVIEW",
        }

    # For other multiple matches, explicitly flag the ambiguity.
    evidence = []

    for _, keywords in matches:
        evidence.append(keywords[0])

    return {
        "category": "Other",
        "priority": priority,
        "reason": (
            "The description contains multiple category signals "
            f"({', '.join(evidence)}), so the category needs review."
        ),
        "flag": "NEEDS_REVIEW",
    }


def batch_classify(input_file, output_file):
    with open(input_file, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            raise ValueError("Input CSV does not contain a header row.")

        required_columns = {
            "complaint_id",
            "date_raised",
            "city",
            "ward",
            "location",
            "description",
            "reported_by",
            "days_open",
        }

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                "Input CSV is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        rows = list(reader)

    if not rows:
        raise ValueError("Input CSV contains no complaint rows.")

    output_columns = list(reader.fieldnames) + [
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_columns)
        writer.writeheader()

        for row in rows:
            result = classify_complaint(row)
            row.update(result)
            writer.writerow(row)

    print(f"Classified {len(rows)} complaints.")
    print(f"Output written to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input complaint CSV",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV",
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()