"""
UC-0A - Complaint Classifier
"""

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
    "gas leak",
]


def classify_complaint(row: dict) -> dict:
    """Classify one citizen complaint."""

    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    # ---------------------------------------------------------
    # Missing description
    # ---------------------------------------------------------

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # ---------------------------------------------------------
    # CATEGORY
    # ---------------------------------------------------------

    # Pothole
    if "pothole" in text or "potholes" in text:
        category = "Pothole"

    # Flooding
    elif any(word in text for word in [
        "flood",
        "flooded",
        "flooding",
        "floods",
        "rainwater",
        "waterlogged",
        "water logging",
        "underpass",
        "flooding risk",
        "channel rainwater",
    ]):
        category = "Flooding"

    # Drain blockage
    elif any(word in text for word in [
        "drain blocked",
        "drain blockage",
        "drain completely blocked",
        "drain is blocked",
        "manhole",
        "stormwater drain",
        "drainage blockage",
        "draining directly onto public road",
    ]):
        category = "Drain Blockage"

    # Streetlight
    elif any(word in text for word in [
        "streetlight",
        "streetlights",
        "lights out",
        "light out",
        "unlit",
        "darkness",
        "dark",
        "lights not working",
        "lighting failure",
        "substation tripped",
    ]):
        category = "Streetlight"

    # Waste
    elif any(word in text for word in [
        "garbage",
        "waste",
        "dumped",
        "trash",
        "rubbish",
        "overflowing bins",
        "waste bins",
    ]):
        category = "Waste"

    # Noise
    elif any(word in text for word in [
        "music",
        "noise",
        "loud",
        "wedding band",
        "drilling",
        "amplifier",
        "amplifiers",
        "engines on",
        "idling",
    ]):
        category = "Noise"

    # Heritage Damage
    elif any(word in text for word in [
        "heritage",
        "historic",
        "historic tram",
        "ancient",
        "heritage stone",
        "tagore museum",
        "heritage building",
        "cobblestones",
    ]):
        category = "Heritage Damage"

    # Heat Hazard
    elif any(word in text for word in [
        "heatwave",
        "heat wave",
        "melting",
        "dangerous temperatures",
        "unbearable",
        "surface temperature",
        "temperature reads",
        "storing heat",
        "extreme heat",
        "surface bubbling",
        "44°c",
        "45°c",
        "52°c",
    ]):
        category = "Heat Hazard"

    # Road Damage
    elif any(word in text for word in [
        "road surface",
        "road subsided",
        "road collapsed",
        "road collapse",
        "road buckled",
        "road cracked",
        "road sinking",
        "road damage",
        "crater",
        "footpath",
        "pavement",
        "tiles broken",
        "broken tiles",
        "road subsidence",
        "surface damage",
    ]):
        category = "Road Damage"

    # Other
    else:
        category = "Other"

    # ---------------------------------------------------------
    # PRIORITY
    # ---------------------------------------------------------

    matched_keywords = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if keyword in text
    ]

    # Urgent
    if matched_keywords:
        priority = "Urgent"

    # Standard
    elif any(word in text for word in [
        "unsafe",
        "dangerous",
        "fall risk",
        "risk",
        "injury risk",
        "inaccessible",
        "abandoned",
        "knee-deep",
        "standing in water",
        "health concern",
        "refusing to use",
        "lights out",
        "light out",
        "unlit",
        "darkness",
        "dark",
        "substation tripped",
        "unbearable",
        "flooding risk",
        "channel rainwater",
        "traders suffering losses",
        "subsidence",
        "temperature reads",
    ]):
        priority = "Standard"

    # Low
    else:
        priority = "Low"

    # ---------------------------------------------------------
    # REASON
    # ---------------------------------------------------------

    if matched_keywords:
        reason = (
            f"The description contains the severity keyword "
            f"'{matched_keywords[0]}'."
        )
    else:
        first_sentence = description.split(".")[0].strip()
        reason = f"The description mentions '{first_sentence}'."

    # ---------------------------------------------------------
    # REVIEW FLAG
    # ---------------------------------------------------------

    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read CSV, classify every row, and write results."""

    results = []

    with open(
        input_path,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as infile:

        reader = csv.DictReader(infile)

        for row in reader:

            try:
                result = classify_complaint(row)

            except Exception as exc:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Unable to classify row: {exc}",
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
        newline="",
        encoding="utf-8"
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