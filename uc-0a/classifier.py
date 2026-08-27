"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

SEVERITY_KEYWORDS = [
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


def classify_complaint(row):
    description = row.get("description", "").lower()

    category_rules = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "flooded", "underpass flooded"],
        "Streetlight": [
            "streetlight",
            "streetlights",
            "lights out",
            "flickering",
            "sparking"
        ],
        "Waste": [
            "garbage",
            "waste",
            "animal",
            "overflowing"
        ],
        "Noise": [
            "music",
            "noise"
        ],
        "Road Damage": [
            "cracked",
            "sinking",
            "broken",
            "footpath",
            "tiles"
        ],
        "Heritage Damage": [
            "heritage"
        ],
        "Heat Hazard": [
            "heat"
        ],
        "Drain Blockage": [
            "drain blocked",
            "manhole"
        ]
    }

    matched_categories = []
    matched_words = {}

    for cat, keywords in category_rules.items():
        kws = [kw for kw in keywords if kw in description]
        if kws:
            matched_categories.append(cat)
            matched_words[cat] = kws

    category = "Other"
    flag = ""
    reason_parts = []

    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_parts.append("No matching category keywords found in description.")
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        all_matches = []
        for cat in matched_categories:
            all_matches.extend(matched_words[cat])
        reason_parts.append(f"Ambiguous description; matched multiple categories ({', '.join(matched_categories)}) on words: " + ", ".join(f"'{w}'" for w in all_matches) + ".")
    else:
        category = matched_categories[0]
        reason_parts.append(f"Classified as {category} because description contains " + " and ".join(f"'{w}'" for w in matched_words[category]) + ".")

    priority = "Standard"
    matched_sev = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    
    if matched_sev:
        priority = "Urgent"
        reason_parts.append(f"Priority set to Urgent due to severity keyword(s): " + ", ".join(f"'{w}'" for w in matched_sev) + ".")
    elif category in ["Flooding", "Drain Blockage"]:
        # Widespread impact typically makes flooding/drain blockage urgent
        priority = "Urgent"
    elif category == "Other":
        priority = "Low"

    reason = " ".join(reason_parts)

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path, output_path):
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                results.append(classify_complaint(row))

            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Row processing failed.",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag"
        ]

        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in results:
            writer.writerow(row)


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

    batch_classify(
        args.input,
        args.output
    )

    print(f"Done. Results written to {args.output}")