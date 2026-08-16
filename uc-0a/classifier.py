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


def get_description(row):
    description = row.get("description", "")

    if description:
        return str(description).strip()

    values = list(row.values())

    if len(values) >= 6:
        return str(values[5]).strip()

    return ""


def classify_category(description):
    text = description.lower()

    # --------------------------------------------------------
    # Heat Hazard
    # --------------------------------------------------------
    if any(word in text for word in [
        "heat",
        "heatwave",
        "heat wave",
        "temperature",
        "temperatures",
        "°c",
        "melting",
        "surface temperature",
        "dangerous temperatures",
        "storing heat",
        "burns on contact",
        "unbearable",
    ]):
        return "Heat Hazard", ""

    # --------------------------------------------------------
    # Streetlight / public lighting
    # --------------------------------------------------------
    if any(word in text for word in [
        "streetlight",
        "street light",
        "streetlights",
        "lights out",
        "light out",
        "unlit",
        "lighting",
        "flickering",
        "sparking",
        "darkness",
        "dark for",
        "substation tripped",
        "power outage",
    ]):
        return "Streetlight", ""

    # --------------------------------------------------------
    # Pothole
    # --------------------------------------------------------
    if any(word in text for word in [
        "pothole",
        "potholes",
    ]):
        return "Pothole", ""

    # --------------------------------------------------------
    # Drain / flooding
    # --------------------------------------------------------
    has_drain = any(word in text for word in [
        "drain blocked",
        "drain completely blocked",
        "100% blocked",
        "drainage blocked",
        "drain blockage",
        "blocked drain",
        "main drain blocked",
        "drain clogged",
        "clogged drain",
        "draining directly onto",
        "draining onto public road",
    ])

    has_flooding = any(word in text for word in [
        "flood",
        "flooded",
        "flooding",
        "floods",
        "flooding risk",
        "waterlogged",
        "water logging",
        "waterlogging",
        "channel rainwater",
    ])

    if has_drain and has_flooding:
        return "Drain Blockage", "NEEDS_REVIEW"

    if has_drain:
        return "Drain Blockage", ""

    if has_flooding:
        return "Flooding", ""

    # --------------------------------------------------------
    # Waste
    # --------------------------------------------------------
    if any(word in text for word in [
        "garbage",
        "waste",
        "rubbish",
        "trash",
        "dumped",
        "dumping",
        "waste bin",
        "waste bins",
        "garbage bin",
        "garbage bins",
        "dead animal",
    ]):
        return "Waste", ""

    # --------------------------------------------------------
    # Noise
    # --------------------------------------------------------
    if any(word in text for word in [
        "noise",
        "loud music",
        "music past",
        "music after",
        "playing music",
        "music audible",
        "club music",
        "sound disturbance",
        "drilling",
        "construction drilling",
        "idling with engines",
        "engines on",
        "amplifiers",
        "amplifier",
        "wedding band",
    ]):
        return "Noise", ""

    # --------------------------------------------------------
    # Heritage Damage
    # --------------------------------------------------------
    heritage_evidence = any(word in text for word in [
        "heritage",
        "historic",
        "historical",
        "heritage building",
        "heritage structure",
        "heritage site",
        "heritage precinct",
        "heritage zone",
        "heritage stone",
        "historic tram",
        "heritage lamp",
        "heritage residential",
    ])

    heritage_damage_evidence = any(word in text for word in [
        "damage",
        "damaged",
        "defaced",
        "knocked over",
        "broken",
        "broken up",
        "removed",
        "not restored",
        "not replaced",
    ])

    if heritage_evidence and heritage_damage_evidence:
        return "Heritage Damage", ""

    # --------------------------------------------------------
    # Road Damage
    # --------------------------------------------------------
    if any(word in text for word in [
        "road surface",
        "road cracked",
        "road crack",
        "road damaged",
        "road damage",
        "road sinking",
        "sinking road",
        "road subsided",
        "road subsidence",
        "subsided",
        "subsidence",
        "broken road",
        "road collapsed",
        "collapsed road",
        "road buckled",
        "crater",
        "footpath",
        "footpath tiles",
        "paving",
        "paving tiles",
        "pavement",
        "upturned paving",
        "broken tiles",
        "manhole",
        "manhole cover",
        "missing manhole",
        "broken bench",
        "shelter roof",
        "roof glass broken",
    ]):
        return "Road Damage", ""

    # --------------------------------------------------------
    # Other / genuinely ambiguous
    # --------------------------------------------------------
    return "Other", "NEEDS_REVIEW"


def find_severity_keyword(description):
    text = description.lower()

    for keyword in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(keyword) + r"\b", text):
            return keyword

    if "collapsed" in text:
        return "collapse"

    return ""


def classify_priority(description):
    severity = find_severity_keyword(description)

    if severity:
        return "Urgent", severity

    return "Standard", ""


def make_reason(description, category, priority, severity):
    clean_description = " ".join(description.split())

    if priority == "Urgent":
        return (
            f'The description states "{clean_description}" and contains '
            f'the severity keyword "{severity}", so the priority is Urgent.'
        )

    if category == "Other":
        return (
            f'The description states "{clean_description}" but does not '
            f'provide enough evidence for a specific allowed category.'
        )

    return (
        f'The description states "{clean_description}", which supports '
        f'the category {category}.'
    )


def classify_complaint(row):
    complaint_id = str(
        row.get("complaint_id", "")
    ).strip()

    description = get_description(row)

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": (
                "The complaint description is missing, so the category "
                "cannot be determined."
            ),
            "flag": "NEEDS_REVIEW",
        }

    category, flag = classify_category(description)

    priority, severity = classify_priority(description)

    reason = make_reason(
        description,
        category,
        priority,
        severity,
    )

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if flag not in ("", "NEEDS_REVIEW"):
        flag = "NEEDS_REVIEW"

    if priority not in ("Urgent", "Standard", "Low"):
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path, output_path):
    results = []

    try:
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

                except Exception as exc:
                    result = {
                        "complaint_id": str(
                            row.get("complaint_id", "")
                        ).strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": (
                            "The complaint row could not be classified "
                            f"because of an input error: {exc}."
                        ),
                        "flag": "NEEDS_REVIEW",
                    }

                results.append(result)

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input CSV was not found: {input_path}"
        )

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as outfile:

        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag",
        ]

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