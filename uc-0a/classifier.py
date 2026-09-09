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


def find_category(description):
    """Classify a complaint using only the approved categories."""

    text = description.lower()

    category_keywords = {
        "Pothole": [
            "pothole",
            "potholes",
        ],
        "Flooding": [
            "flooded",
            "flooding",
            "flood",
            "waterlogged",
            "water logging",
            "inaccessible due to water",
        ],
        "Streetlight": [
            "streetlight",
            "street light",
            "streetlights",
            "lamp post",
            "lamp",
        ],
        "Waste": [
            "garbage",
            "waste",
            "trash",
            "rubbish",
            "dumped",
            "dumping",
        ],
        "Noise": [
            "noise",
            "noisy",
            "loud music",
            "music past midnight",
        ],
        "Road Damage": [
            "road surface cracked",
            "road surface",
            "cracked road",
            "cracked",
            "sinking road",
            "road is damaged",
            "damaged road",
            "broken road",
            "road damage",
        ],
        "Heritage Damage": [
            "heritage",
            "historic building",
            "historic structure",
            "monument",
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
            "drainage blocked",
        ],
    }

    matches = []

    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in text:
                matches.append(category)
                break

    # A complaint explicitly mentioning a blocked drain is
    # classified as Drain Blockage unless the complaint is clearly
    # about flooding itself without a blockage.
    if "drain blocked" in text or "blocked drain" in text:
        if "flooded" in text or "flooding" in text:
            return "Drain Blockage", ""

    # If exactly one category is supported, use it.
    if len(matches) == 1:
        return matches[0], ""

    # If multiple categories are supported, flag genuine ambiguity.
    if len(matches) > 1:
        return "Other", "NEEDS_REVIEW"

    return "Other", ""


def find_priority(description):
    """Return Urgent when any required severity keyword is present."""

    text = description.lower()

    found_keywords = []

    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            found_keywords.append(keyword)

    if found_keywords:
        return "Urgent", found_keywords

    return "Standard", []


def make_reason(description, category, priority, severity_keywords):
    """Create exactly one sentence citing words from the description."""

    text = description.lower()

    if severity_keywords:
        words = ", ".join(f"'{word}'" for word in severity_keywords)
        return (
            f"The description contains the severity keyword(s) {words}, "
            f"so the complaint is classified as Urgent."
        )

    if category == "Other":
        return (
            f"The description does not contain a sufficiently specific "
            f"approved category term, so it is classified as Other."
        )

    category_terms = {
        "Pothole": ["pothole", "potholes"],
        "Flooding": ["flooded", "flooding", "flood"],
        "Streetlight": ["streetlight", "streetlights", "street light"],
        "Waste": ["garbage", "waste", "trash", "rubbish", "dumped"],
        "Noise": ["noise", "noisy", "loud music", "music past midnight"],
        "Road Damage": [
            "road surface cracked",
            "cracked",
            "sinking",
            "damaged road",
            "broken road",
        ],
        "Heritage Damage": ["heritage", "historic building", "monument"],
        "Heat Hazard": ["heat hazard", "extreme heat", "heatwave", "heat wave"],
        "Drain Blockage": [
            "drain blocked",
            "blocked drain",
            "drain blockage",
            "clogged drain",
        ],
    }

    cited_terms = []

    for term in category_terms.get(category, []):
        if term in text:
            cited_terms.append(term)

    if cited_terms:
        cited = ", ".join(f"'{term}'" for term in cited_terms)
        return f"The description contains {cited}, supporting the {category} category."

    return f"The description supports the {category} category."


def classify_complaint(description):
    """
    Classify one complaint into:
    category, priority, reason, flag
    """

    if not description or not description.strip():
        raise ValueError("Complaint description is empty.")

    category, flag = find_category(description)
    priority, severity_keywords = find_priority(description)

    reason = make_reason(
        description,
        category,
        priority,
        severity_keywords,
    )

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    """Read the input CSV, classify every complaint, and write results."""

    try:
        with open(
            input_file,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError("Input CSV has no header.")

            description_column = None

            for column in reader.fieldnames:
                if column.lower() in {
                    "description",
                    "complaint",
                    "complaint_description",
                    "text",
                }:
                    description_column = column
                    break

            if description_column is None:
                raise ValueError(
                    "Input CSV does not contain a description column."
                )

            rows = list(reader)

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )
    except OSError as error:
        raise OSError(
            f"Could not read input file: {error}"
        )

    output_rows = []

    for row in rows:
        description = (row.get(description_column) or "").strip()

        if not description:
            raise ValueError(
                "A complaint description is missing. "
                "Classification cannot be guessed."
            )

        category, priority, reason, flag = classify_complaint(
            description
        )

        if category not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Invalid category generated: {category}"
            )

        if priority not in {"Urgent", "Standard", "Low"}:
            raise ValueError(
                f"Invalid priority generated: {priority}"
            )

        if flag not in {"", "NEEDS_REVIEW"}:
            raise ValueError(
                f"Invalid flag generated: {flag}"
            )

        result = dict(row)
        result["category"] = category
        result["priority"] = priority
        result["reason"] = reason
        result["flag"] = flag

        output_rows.append(result)

    fieldnames = list(reader.fieldnames)

    for field in ["category", "priority", "reason", "flag"]:
        if field not in fieldnames:
            fieldnames.append(field)

    try:
        with open(
            output_file,
            "w",
            encoding="utf-8",
            newline=""
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(output_rows)

    except OSError as error:
        raise OSError(
            f"Could not write output file: {error}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Classify citizen complaints."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input complaint CSV."
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output CSV."
    )

    args = parser.parse_args()

    batch_classify(
        args.input,
        args.output
    )

    print(
        f"Classification completed successfully: {args.output}"
    )


if __name__ == "__main__":
    main()