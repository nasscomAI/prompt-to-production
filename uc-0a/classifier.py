"""
UC-0A — Complaint Classifier
RICE-enforced deterministic implementation.
"""

import argparse
import csv


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

URGENT_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)


def classify_complaint(row: dict) -> dict:
    """Classify one complaint using only its description."""

    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or invalid.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Fixed category rules. More specific categories are checked first.
    category = "Other"

    if "heritage" in text:
        category = "Heritage Damage"
    elif "drain" in text and "blocked" in text:
        category = "Drain Blockage"
    elif "streetlight" in text:
        category = "Streetlight"
    elif "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "flooded" in text or "water" in text:
        category = "Flooding"
    elif "garbage" in text or "waste" in text or "dumped" in text:
        category = "Waste"
    elif "music" in text or "noise" in text:
        category = "Noise"
    elif "road surface" in text or "road" in text and (
        "cracked" in text or "sinking" in text
    ):
        category = "Road Damage"
    elif "heat" in text or "hot" in text:
        category = "Heat Hazard"

    # Ambiguous/unclassifiable complaints require review.
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Severity keywords always trigger Urgent.
    urgent_word = next(
        (word for word in URGENT_KEYWORDS if word in text),
        None,
    )
    if urgent_word:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Reason must cite specific words from the description.
    if category == "Other":
        reason = f'The description contains "{description[:80]}" but does not clearly match an allowed category.'
    elif urgent_word:
        reason = (
            f'The complaint is classified as {category} because the description '
            f'contains "{urgent_word}", which requires Urgent priority.'
        )
    else:
        evidence = {
            "Pothole": "pothole",
            "Flooding": "flood",
            "Streetlight": "streetlight",
            "Waste": "waste",
            "Noise": "music",
            "Road Damage": "cracked",
            "Heritage Damage": "heritage",
            "Heat Hazard": "heat",
            "Drain Blockage": "drain",
        }

        keyword = evidence.get(category, category.lower())
        reason = (
            f'The complaint is classified as {category} because the '
            f'description contains "{keyword}".'
        )

    # Final schema enforcement.
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read CSV, classify every row, and always produce an output CSV."""

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    results = []

    try:
        with open(input_path, "r", newline="", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                try:
                    results.append(classify_complaint(row))
                except Exception as exc:
                    results.append(
                        {
                            "complaint_id": str(row.get("complaint_id", "")).strip(),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f"Classification failed: {exc}",
                            "flag": "NEEDS_REVIEW",
                        }
                    )

    except Exception as exc:
        results.append(
            {
                "complaint_id": "",
                "category": "Other",
                "priority": "Standard",
                "reason": f"Input could not be read: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        )

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


