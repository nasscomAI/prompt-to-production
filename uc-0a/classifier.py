import argparse
import csv

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

URGENT_WORDS = [
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


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").strip()
    text = description.lower()

    # Classify category using specific evidence from the description.
    if "pothole" in text:
        category = "Pothole"
        evidence = "pothole"

    elif "flood" in text or "flooding" in text:
        category = "Flooding"
        evidence = "flooded" if "flooded" in text else "flood"

    elif "streetlight" in text or "street light" in text:
        category = "Streetlight"
        evidence = "streetlight"

    elif "garbage" in text or "waste" in text or "dumped" in text:
        category = "Waste"
        evidence = (
            "garbage"
            if "garbage" in text
            else "waste"
            if "waste" in text
            else "dumped"
        )

    elif "noise" in text or "loud music" in text or "music" in text:
        category = "Noise"
        evidence = "loud music" if "loud music" in text else "music"

    elif (
        "road damage" in text
        or "road surface" in text
        or "cracked" in text
        or "sinking" in text
        or "footpath" in text
        or "tiles broken" in text
    ):
        category = "Road Damage"
        if "road surface" in text:
            evidence = "road surface cracked and sinking"
        elif "footpath" in text:
            evidence = "footpath tiles broken"
        elif "sinking" in text:
            evidence = "sinking"
        else:
            evidence = "cracked"

    elif "heritage" in text:
        category = "Heritage Damage"
        evidence = "heritage"

    elif "heat" in text:
        category = "Heat Hazard"
        evidence = "heat"

    elif "drain" in text or "manhole" in text:
        category = "Drain Blockage"
        evidence = "drain" if "drain" in text else "manhole"

    else:
        category = "Other"
        evidence = None

    # Urgent if any required severity keyword is present.
    urgent_word = next(
        (word for word in URGENT_WORDS if word in text),
        None
    )

    priority = "Urgent" if urgent_word else "Standard"

    # Every reason must cite specific evidence from the description.
    if urgent_word and evidence:
        reason = (
            f'The description contains "{evidence}" and the severity '
            f'keyword "{urgent_word}", so this is {category}.'
        )
    elif urgent_word:
        reason = (
            f'The description contains the severity keyword '
            f'"{urgent_word}", so the priority is Urgent.'
        )
    elif evidence:
        reason = (
            f'The description contains "{evidence}", so the category '
            f'is {category}.'
        )
    else:
        reason = (
            "The description does not provide enough evidence for a "
            "specific allowed category."
        )

    # Genuinely unclear category requires review.
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": (
                        "The complaint could not be classified from "
                        "the available description."
                    ),
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", encoding="utf-8", newline="") as file:
        fields = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag",
        ]

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


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