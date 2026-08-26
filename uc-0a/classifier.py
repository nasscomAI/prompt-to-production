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

SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fall",
    "fell",
    "collapse",
)


CATEGORY_PATTERNS = {
    "Pothole": (
        r"\bpothole\b",
        r"\bpotholes\b",
    ),

    "Flooding": (
        r"\bflood(?:ed|ing)?\b",
        r"\bfloods\b",
        r"\brainwater\b",
        r"\bwater[- ]logged\b",
        r"\bwaterlogging\b",
        r"\bstranded\b",
        r"\binaccessible\b",
    ),

    "Streetlight": (
        r"\bstreetlights?\b",
        r"\bunlit\b",
        r"\blights?\s+out\b",
        r"\bflickering\b",
        r"\bsparking\b",
        r"\bdarkness\b",
    ),

    "Waste": (
        r"\bgarbage\b",
        r"\bwaste\b",
        r"\btrash\b",
        r"\brubbish\b",
        r"\bdumped\b",
        r"\bdumping\b",
        r"\boverflowing\b.*\bbins?\b",
        r"\bdead animal\b",
    ),

    "Noise": (
        r"\bnoise\b",
        r"\bmusic\b",
        r"\bwedding band\b",
        r"\bamplifiers?\b",
        r"\bamplifier\b",
        r"\bdrilling\b",
        r"\bidling\b.*\bengines?\b",
        r"\bengines?\s+on\b",
    ),

    "Road Damage": (
        r"\broad surface\b",
        r"\broad\b.*\bcracked\b",
        r"\broad\b.*\bsinking\b",
        r"\broad\b.*\bsubsided\b",
        r"\broad\b.*\bcollapsed\b",
        r"\broad\b.*\bbuckled\b",
        r"\broad\b.*\bcrater\b",
        r"\bfootpath\b",
        r"\bsidewalk\b",
        r"\bpaving\b",
        r"\btiles?\b.*\bbroken\b",
        r"\bupturned paving\b",
        r"\bmanhole cover\b",
        r"\bbridge approach\b",
    ),

    "Heritage Damage": (
        r"\bheritage\b",
        r"\bhistoric\b",
        r"\bold city\b",
        r"\bheritage zone\b",
        r"\bheritage precinct\b",
        r"\bheritage stone\b",
        r"\btagore museum\b",
        r"\btram road\b",
        r"\bheritage residential\b",
        r"\bancient step well\b",
    ),

    "Heat Hazard": (
        r"\bheatwave\b",
        r"\bheat\b",
        r"\btemperature\b",
        r"\b\d+\s*°?\s*c\b",
        r"\bmelting\b",
        r"\bburns?\b",
        r"\bfull sun\b",
        r"\bunbearable\b",
        r"\bdangerous temperatures?\b",
    ),

    "Drain Blockage": (
        r"\bdrain\b.*\bblocked\b",
        r"\bblocked\b.*\bdrain\b",
        r"\bdrain\b.*\bblockage\b",
        r"\bstormwater drain\b",
        r"\bmain drain\b",
        r"\bmosquito breeding\b",
    ),
}


def _find_evidence(description, patterns):
    """Return the first directly matching phrase from the description."""
    for pattern in patterns:
        match = re.search(pattern, description, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def _classify_category(description):
    """Classify using evidence scores and explicit ambiguity handling."""
    matches = {}

    for category, patterns in CATEGORY_PATTERNS.items():
        evidence = _find_evidence(description, patterns)
        if evidence:
            matches[category] = evidence

    if not matches:
        return "Other", None, "NEEDS_REVIEW"

    # Heritage-specific physical damage should be Heritage Damage.
    heritage_words = (
        "heritage",
        "historic",
        "heritage stone",
        "old city",
        "tram road",
        "tagore museum",
        "ancient step well",
    )

    heritage_damage_words = (
        "broken",
        "defaced",
        "removed",
        "knocked over",
        "subsided",
        "not replaced",
        "damaged",
    )

    lower = description.lower()

    if (
        "Heritage Damage" in matches
        and any(word in lower for word in heritage_words)
        and any(word in lower for word in heritage_damage_words)
    ):
        return "Heritage Damage", matches["Heritage Damage"], ""

    # A blocked drain is distinct from a flooding event when the complaint
    # explicitly focuses on the blocked drain.
    if "Drain Blockage" in matches and "Flooding" not in matches:
        return "Drain Blockage", matches["Drain Blockage"], ""

    # If both flooding and a blocked drain are present, an explicit
    # flooding event is treated as the primary complaint.
    if "Flooding" in matches and "Drain Blockage" in matches:
        if any(
            phrase in lower
            for phrase in (
                "flooding risk",
                "at flooding risk",
                "flooded",
                "flooding",
                "floods",
            )
        ):
            return "Flooding", matches["Flooding"], ""

    # A clear flooding event takes precedence over generic road-location
    # evidence such as "bridge approach".
    if "Flooding" in matches:
        return "Flooding", matches["Flooding"], ""

    # Heritage context alone does not make waste, noise, or streetlight
    # complaints Heritage Damage.
    non_context_matches = {
        category: evidence
        for category, evidence in matches.items()
        if category != "Heritage Damage"
    }

    if len(non_context_matches) == 1:
        category, evidence = next(iter(non_context_matches.items()))
        return category, evidence, ""

    # Heat-related descriptions can be unambiguous even when they mention
    # exposed infrastructure such as shelters or road surfaces.
    if "Heat Hazard" in matches:
        return "Heat Hazard", matches["Heat Hazard"], ""

    # Explicit pothole evidence wins over generic road-surface wording.
    if "Pothole" in matches:
        return "Pothole", matches["Pothole"], ""

    # Streetlight complaints remain Streetlight even in heritage areas.
    if "Streetlight" in matches:
        return "Streetlight", matches["Streetlight"], ""

    # Waste complaints remain Waste even when the area is described as heritage.
    if "Waste" in matches:
        return "Waste", matches["Waste"], ""

    # Noise complaints remain Noise even when the location is heritage.
    if "Noise" in matches:
        return "Noise", matches["Noise"], ""

    # Road damage is the remaining explicit physical-road category.
    if "Road Damage" in matches:
        return "Road Damage", matches["Road Damage"], ""

    if len(matches) == 1:
        category, evidence = next(iter(matches.items()))
        return category, evidence, ""

    return "Other", None, "NEEDS_REVIEW"


def _priority(description):
    """Apply the mandatory severity keyword rule."""
    lower = description.lower()

    # Use substring matching so required triggers such as "collapse",
    # "collapsed", "child", and "children" are all detected.
    for keyword in SEVERITY_KEYWORDS:
        if keyword in lower:
            return "Urgent"

    return "Standard"


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns exactly:
    complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        return {
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": (
                "The complaint row is invalid and contains no usable "
                "description."
            ),
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = str(row.get("complaint_id", "") or "").strip()
    description = str(row.get("description", "") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    category, evidence, flag = _classify_category(description)
    priority = _priority(description)

    if evidence:
        reason = (
            f'The description contains "{evidence}", supporting the '
            f"{category} category."
        )
    else:
        reason = (
            "The description does not provide enough evidence for one "
            "allowed category, so it requires review."
        )

    return {
        "complaint_id": complaint_id,
        "category": (
            category if category in ALLOWED_CATEGORIES else "Other"
        ),
        "priority": (
            priority
            if priority in {"Urgent", "Standard", "Low"}
            else "Standard"
        ),
        "reason": reason,
        "flag": (
            flag
            if flag in {"", "NEEDS_REVIEW"}
            else "NEEDS_REVIEW"
        ),
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read an input CSV, classify every row, and always attempt to produce
    the requested output CSV.
    """
    fieldnames = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    results = []

    try:
        with open(
            input_path,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                try:
                    results.append(classify_complaint(row))
                except Exception as exc:
                    results.append(
                        {
                            "complaint_id": str(
                                row.get("complaint_id", "")
                            ).strip(),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": (
                                "Classification failed safely because "
                                f"the row could not be processed: {exc}."
                            ),
                            "flag": "NEEDS_REVIEW",
                        }
                    )

    except Exception as exc:
        results.append(
            {
                "complaint_id": "",
                "category": "Other",
                "priority": "Standard",
                "reason": (
                    "The input file could not be processed: "
                    f"{exc}."
                ),
                "flag": "NEEDS_REVIEW",
            }
        )

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
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

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")