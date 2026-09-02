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

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}
ALLOWED_FLAGS = {"", "NEEDS_REVIEW"}

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

CATEGORY_PRECEDENCE = [
    "Pothole",
    "Drain Blockage",
    "Flooding",
    "Streetlight",
    "Heritage Damage",
    "Road Damage",
    "Waste",
    "Noise",
    "Heat Hazard",
    "Other",
]

CATEGORY_PATTERNS = {
    "Pothole": [
        "pothole",
        "potholes",
    ],
    "Drain Blockage": [
        "drain blocked",
        "blocked drain",
        "drainage blocked",
        "clogged drain",
    ],
    "Flooding": [
        "flood",
        "flooded",
        "knee-deep",
        "bridge inaccessible",
    ],
    "Streetlight": [
        "streetlight",
        "streetlights",
        "lights out",
        "light out",
        "flicker",
        "flickering",
        "sparking",
        "sparks",
    ],
    "Heritage Damage": [
        "heritage",
        "heritage street",
        "heritage building",
    ],
    "Waste": [
        "garbage",
        "overflowing garbage",
        "overflowing bins",
        "overflowing",
        "bins",
        "bulk waste",
        "dumped",
        "dumping",
        "dead animal",
        "dead animal not removed",
    ],
    "Noise": [
        "music",
        "playing music",
        "noise",
        "loud",
        "past midnight",
    ],
    "Road Damage": [
        "crack",
        "cracked",
        "sinking",
        "subsidence",
        "footpath tiles broken",
        "tiles broken",
        "upturned",
        "manhole cover missing",
        "manhole missing",
        "manhole cover",
    ],
    "Heat Hazard": [
        "heatwave",
        "heat hazard",
        "high temperature",
    ],
}


def normalize(text):
    """Normalize text for case-insensitive matching."""
    text = str(text or "").lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip(" .,;:!?\"'()[]{}")


def find_matches(description):
    """Return matched category evidence."""
    text = normalize(description)
    matches = {}

    for category, patterns in CATEGORY_PATTERNS.items():
        found = []

        for pattern in patterns:
            if pattern.lower() in text:
                found.append(pattern)

        if found:
            matches[category] = found

    return matches


def contains_severity_keyword(description):
    """Check the exact required severity keyword list."""
    text = normalize(description)

    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            return keyword

    return None


def determine_priority(description, category):
    """Determine priority using the deterministic rules."""
    text = normalize(description)

    # Step 1: severity override
    severity = contains_severity_keyword(text)

    if severity:
        return "Urgent", severity

    # Step 2: category-specific urgent triggers

    if category == "Streetlight":
        for phrase in ["sparking", "sparks", "electrical hazard"]:
            if phrase in text:
                return "Urgent", phrase

    if category == "Pothole":
        for phrase in [
            "tyre",
            "tire",
            "vehicle",
            "vehicles",
            "car",
            "bike",
            "cyclist",
            "bicycle",
        ]:
            if phrase in text:
                return "Urgent", phrase

    if category in {"Flooding", "Drain Blockage"}:
        for phrase in [
            "stranded",
            "impassable",
            "inaccessible",
            "commuters stranded",
            "bridge inaccessible",
        ]:
            if phrase in text:
                return "Urgent", phrase

    if category == "Road Damage":
        if "fell" in text:
            return "Urgent", "fell"

    # Step 3: Standard vs Low
    standard_indicators = [
        "risk",
        "blocked",
        "overflow",
        "overflowing",
        "obstruction",
        "smell",
        "flood",
        "flooded",
        "dark",
        "broken",
        "upturned",
        "cracked",
        "sinking",
        "missing",
    ]

    for indicator in standard_indicators:
        if indicator in text:
            return "Standard", indicator

    return "Low", None


def make_reason(description, category_evidence, priority_evidence):
    """Create exactly one sentence using quoted evidence from description."""
    original = str(description or "")

    quoted = []

    if category_evidence:
        phrase = category_evidence[0]

        # Find the original text matching the phrase, preserving capitalization.
        match = re.search(re.escape(phrase), original, re.IGNORECASE)

        if match:
            quoted.append(match.group(0))

    if priority_evidence:
        match = re.search(
            re.escape(priority_evidence),
            original,
            re.IGNORECASE,
        )

        if match:
            actual = match.group(0)

            if actual.lower() not in [x.lower() for x in quoted]:
                quoted.append(actual)

    if quoted:
        evidence = " and ".join(f'"{item}"' for item in quoted)
        return f"The description mentions {evidence}."

    # Fallback for invalid/missing descriptions.
    return 'The description does not contain a clear mapped category.'


def classify_complaint(row):
    """
    Classify a single complaint.

    Returns exactly:
    category, priority, reason, flag
    """

    description = str(row.get("description", "") or "")
    text = normalize(description)

    matches = find_matches(description)
    matched_categories = list(matches.keys())

    # Determine category
    if not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
        category_evidence = []
    else:
        category = next(
            cat for cat in CATEGORY_PRECEDENCE
            if cat in matched_categories
        )

        category_evidence = matches[category]

        if len(matched_categories) > 1:
            flag = "NEEDS_REVIEW"
        else:
            flag = ""

    # Short description rule
    word_count = len(text.split())

    if word_count < 5 and not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority
    priority, priority_evidence = determine_priority(
        description,
        category,
    )

    # Reason
    reason = make_reason(
        description,
        category_evidence,
        priority_evidence,
    )

    result = {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

    # Validation
    if result["category"] not in ALLOWED_CATEGORIES:
        raise ValueError(f"Invalid category: {result['category']}")

    if result["priority"] not in ALLOWED_PRIORITIES:
        raise ValueError(f"Invalid priority: {result['priority']}")

    if result["flag"] not in ALLOWED_FLAGS:
        raise ValueError(f"Invalid flag: {result['flag']}")

    if not result["reason"]:
        raise ValueError("Reason cannot be empty")

    return result


def batch_classify(input_path, output_path):
    """
    Read input CSV, classify every row, and write results CSV.
    """

    with open(input_path, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header")

        if "description" not in reader.fieldnames:
            raise ValueError("Input CSV must contain a description column")

        original_columns = list(reader.fieldnames)
        rows = list(reader)

    output_columns = original_columns + [
        "category",
        "priority",
        "reason",
        "flag",
    ]

    results = []

    for row in rows:
        try:
            classification = classify_complaint(row)
        except Exception:
            classification = {
                "category": "Other",
                "priority": "Low",
                "reason": 'The description does not contain a clear mapped category.',
                "flag": "NEEDS_REVIEW",
            }

        output_row = dict(row)
        output_row.update(classification)
        results.append(output_row)

    # Validate row count
    if len(results) != len(rows):
        raise ValueError("Output row count does not match input row count")

    # Write output
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=output_columns,
            extrasaction="raise",
        )

        writer.writeheader()

        for result in results:
            writer.writerow(result)

    # Final validation
    if len(output_columns) != len(original_columns) + 4:
        raise ValueError("Incorrect output column count")

    if output_columns[-4:] != [
        "category",
        "priority",
        "reason",
        "flag",
    ]:
        raise ValueError("Incorrect appended columns")


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