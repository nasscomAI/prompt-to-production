import argparse
import csv


# ============================================================
# UC-0A COMPLAINT CLASSIFIER
# ============================================================

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


# These keywords MUST trigger Urgent priority.
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


def classify_complaint(row: dict) -> dict:
    """
    Classify one citizen complaint.

    Returns:
        complaint_id
        category
        priority
        reason
        flag
    """

    complaint_id = row.get("complaint_id", "")
    description = str(row.get("description", "")).strip()

    # --------------------------------------------------------
    # Missing description
    # --------------------------------------------------------

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The complaint description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # --------------------------------------------------------
    # PRIORITY
    # --------------------------------------------------------

    matched_severity = next(
        (word for word in SEVERITY_KEYWORDS if word in text),
        None
    )

    priority = "Urgent" if matched_severity else "Standard"

    # --------------------------------------------------------
    # CATEGORY CLASSIFICATION
    # --------------------------------------------------------

    # 1. POTHOLE
    if any(word in text for word in [
        "pothole",
        "potholes",
    ]):
        category = "Pothole"
        reason = (
            'The description contains "pothole", '
            'indicating Pothole.'
        )

    # 2. FLOODING
    elif any(word in text for word in [
        "flooded",
        "flooding",
        "flood",
        "waterlogged",
        "water logging",
    ]):
        category = "Flooding"
        reason = (
            'The description contains "flood", '
            'indicating Flooding.'
        )

    # 3. STREETLIGHT
    elif any(word in text for word in [
        "streetlight",
        "street light",
        "street lights",
        "lights out",
        "lamp post",
        "unlit",
        "darkness",
        "dark for",
    ]):
        category = "Streetlight"
        reason = (
            'The description contains streetlight-related '
            'terms such as "streetlight", "lights out", '
            'or "unlit", indicating Streetlight.'
        )

    # 4. WASTE
    elif any(word in text for word in [
        "garbage",
        "waste",
        "trash",
        "litter",
        "dumped",
        "dead animal",
        "waste bins",
        "waste bin",
        "waste overflowing",
    ]):
        category = "Waste"
        reason = (
            'The description contains a waste-related term, '
            'indicating Waste.'
        )

    # 5. NOISE
    elif any(word in text for word in [
        "noise",
        "loud music",
        "loudspeaker",
        "music past midnight",
        "club music",
        "sound pollution",
        "wedding band",
        "amplifiers",
        "amplifier",
    ]):
        category = "Noise"
        reason = (
            'The description contains a noise-related term '
            'such as music, amplifiers, or loud sound, '
            'indicating Noise.'
        )

    # 6. HEAT HAZARD
    #
    # Checked before Road Damage because some complaints
    # mention road surfaces but the actual problem is heat.
    elif any(word in text for word in [
        "heat hazard",
        "extreme heat",
        "heatwave",
        "heat wave",
        "heatwave conditions",
        "dangerous temperatures",
        "temperature unbearable",
        "surface temperature",
        "storing heat",
        "heat exposure",
        "44°c",
        "45°c",
        "52°c",
        "melting at",
    ]):
        category = "Heat Hazard"
        reason = (
            'The description contains heat-related conditions '
            'such as high temperature or heatwave, '
            'indicating Heat Hazard.'
        )

    # 7. HERITAGE DAMAGE
    #
    # Checked before Road Damage because roads/paving can occur
    # inside heritage areas and the heritage issue takes priority
    # when explicitly stated.
    elif any(word in text for word in [
        "heritage damage",
        "heritage structure",
        "heritage lamp post",
        "heritage residential",
        "heritage stone",
        "heritage concern",
        "monument damage",
        "historical site damage",
        "historic tram",
        "historic",
        "ancient step well",
        "tagore museum",
        "marble palace",
        "defaced",
    ]):
        category = "Heritage Damage"
        reason = (
            'The description contains heritage-related terms '
            'such as "heritage", "historic", or "heritage stone", '
            'indicating Heritage Damage.'
        )

    # 8. ROAD DAMAGE
    elif any(word in text for word in [
        "road surface cracked",
        "cracked road",
        "damaged road",
        "broken road",
        "road surface",
        "road subsidence",
        "road subsided",
        "road surface buckled",
        "sinking",
        "footpath",
        "tiles broken",
        "tiles upturned",
        "upturned paving",
        "paving broken",
        "paving",
        "surface bubbling",
    ]):
        category = "Road Damage"
        reason = (
            'The description contains road or paving damage, '
            'indicating Road Damage.'
        )

    # 9. DRAIN BLOCKAGE
    elif any(word in text for word in [
        "drain blocked",
        "blocked drain",
        "clogged drain",
        "drainage blockage",
        "draining directly onto public road",
        "draining onto public road",
        "manhole",
    ]):
        category = "Drain Blockage"
        reason = (
            'The description contains drain or drainage-related '
            'information, indicating Drain Blockage.'
        )

    # 10. OTHER
    else:
        category = "Other"
        reason = (
            "The description does not contain enough "
            "category-specific information to determine a category."
        )

    # --------------------------------------------------------
    # FINAL ENFORCEMENT
    # --------------------------------------------------------

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        flag = "" if category != "Other" else "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ============================================================
# BATCH CLASSIFICATION
# ============================================================

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify every row, and write output CSV.

    Invalid rows should not crash the complete batch.
    """

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
                raise ValueError("Input CSV has no header.")

            for row in reader:

                try:
                    result = classify_complaint(row)

                except Exception as exc:
                    result = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": (
                            f"Classification failed safely: {exc}."
                        ),
                        "flag": "NEEDS_REVIEW",
                    }

                results.append(result)

    except (OSError, csv.Error, ValueError) as exc:
        print(f"Error reading input file: {exc}")
        return

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    try:
        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as outfile:

            writer = csv.DictWriter(
                outfile,
                fieldnames=output_fields
            )

            writer.writeheader()
            writer.writerows(results)

    except OSError as exc:
        print(f"Error writing output file: {exc}")
        return


# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

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