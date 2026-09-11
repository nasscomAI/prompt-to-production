"""
UC-0A – Complaint Classifier

Classifies citizen complaints using deterministic keyword-based rules.
"""

import argparse
import csv


# Exact categories allowed by the UC-0A requirements.
CATEGORIES = [
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


# Keywords that make a complaint Urgent.
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


# Category keywords.
CATEGORY_MATCHERS = {
    "Pothole": [
        "pothole",
        "potholes",
    ],

    "Flooding": [
        "flood",
        "flooding",
        "waterlogged",
        "water logging",
    ],

    "Streetlight": [
        "streetlight",
        "street light",
        "street lights",
        "lamp post",
        "street lamp",
        "lights out",
    ],

    "Waste": [
        "waste",
        "garbage",
        "trash",
        "rubbish",
        "dump",
        "dumped",
        "bin",
        "bins",
        "waste overflowing",
        "garbage overflowing",
    ],

    "Noise": [
        "noise",
        "noisy",
        "loud music",
        "music",
        "loud sound",
        "engines idling",
    ],

    "Road Damage": [
        "road damage",
        "road damaged",
        "broken road",
        "damaged road",
        "road surface",
        "road sinking",
        "sinking road",
        "road crack",
        "cracked road",
        "cracks in road",
        "footpath",
        "footpath broken",
        "footpath damaged",
        "broken footpath",
        "pavement",
        "pavement broken",
        "pavement damaged",
        "tiles broken",
    ],

    "Heritage Damage": [
        "heritage",
        "heritage site",
        "monument",
        "historical building",
        "historic building",
    ],

    "Heat Hazard": [
        "heat",
        "extreme heat",
        "heat hazard",
        "heatwave",
        "heat wave",
    ],

    "Drain Blockage": [
        "drain blocked",
        "blocked drain",
        "drain blockage",
        "drain clogged",
        "clogged drain",
        "sewer blocked",
        "sewer blockage",
        "manhole",
        "manhole cover",
    ],
}


def classify_complaint(row):
    """
    Classify one citizen complaint.
    """

    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Missing description.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description was provided.",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()

    # ---------------------------------------------------------
    # STEP 1: Determine priority
    # ---------------------------------------------------------

    priority = "Standard"

    for keyword in URGENT_KEYWORDS:
        if keyword in description_lower:
            priority = "Urgent"
            break

    # ---------------------------------------------------------
    # STEP 2: Find category matches
    # ---------------------------------------------------------

    matches = []

    for category, keywords in CATEGORY_MATCHERS.items():

        for keyword in keywords:

            if keyword in description_lower:
                matches.append((category, keyword))
                break

    # ---------------------------------------------------------
    # STEP 3: No category found
    # ---------------------------------------------------------

    if not matches:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": "No allowed category keyword was found in the description.",
            "flag": "NEEDS_REVIEW",
        }

    # ---------------------------------------------------------
    # STEP 4: Remove duplicate categories
    # ---------------------------------------------------------

    unique_matches = []
    seen_categories = set()

    for category, keyword in matches:

        if category not in seen_categories:
            unique_matches.append((category, keyword))
            seen_categories.add(category)

    # ---------------------------------------------------------
    # STEP 5: If multiple categories match,
    # choose the most specific category.
    # ---------------------------------------------------------

    if len(unique_matches) > 1:

        preferred_order = [
            "Drain Blockage",
            "Pothole",
            "Road Damage",
            "Streetlight",
            "Waste",
            "Noise",
            "Heritage Damage",
            "Heat Hazard",
            "Flooding",
        ]

        selected_match = None

        for preferred_category in preferred_order:

            for category, keyword in unique_matches:

                if category == preferred_category:
                    selected_match = (category, keyword)
                    break

            if selected_match:
                break

        if selected_match:

            category, keyword = selected_match

            return {
                "complaint_id": complaint_id,
                "category": category,
                "priority": priority,
                "reason": f'The description contains "{keyword}", indicating {category}.',
                "flag": "",
            }

        # Genuine ambiguity.
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": "The description contains multiple category indicators and is ambiguous.",
            "flag": "NEEDS_REVIEW",
        }

    # ---------------------------------------------------------
    # STEP 6: Exactly one category matched
    # ---------------------------------------------------------

    category, keyword = unique_matches[0]

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": f'The description contains "{keyword}", indicating {category}.',
        "flag": "",
    }


def batch_classify(input_path, output_path):
    """
    Read complaints from CSV and write classified results.
    """

    results = []

    # ---------------------------------------------------------
    # Read input CSV
    # ---------------------------------------------------------

    with open(
        input_path,
        mode="r",
        newline="",
        encoding="utf-8"
    ) as infile:

        reader = csv.DictReader(infile)

        for row in reader:

            try:

                classified = classify_complaint(row)
                results.append(classified)

            except Exception:

                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Error processing this complaint.",
                    "flag": "NEEDS_REVIEW",
                })

    # ---------------------------------------------------------
    # Output columns
    # ---------------------------------------------------------

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    # ---------------------------------------------------------
    # Write output CSV
    # ---------------------------------------------------------

    with open(
        output_path,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=output_fields
        )

        writer.writeheader()

        for result in results:
            writer.writerow(result)

    print(
        f"Batch classification complete. Written to {output_path}"
    )


def main():
    """
    Command-line entry point.
    """

    parser = argparse.ArgumentParser(
        description="Classify citizen complaints."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file."
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output CSV file."
    )

    args = parser.parse_args()

    try:

        batch_classify(
            args.input,
            args.output
        )

    except Exception as exc:

        print(
            f"Error during batch classification: {exc}"
        )


if __name__ == "__main__":
    main()