"""Deterministic UC-0A citizen complaint classifier."""

import argparse
import csv
import re


OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]
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
URGENT_TRIGGERS = (
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

# Longer phrases are checked before their component words so that the
# evidence in a reason is specific and stable.
CATEGORY_EVIDENCE = {
    "Pothole": ("pothole", "potholes"),
    "Flooding": ("flooded", "flooding", "floods", "flood"),
    "Streetlight": (
        "streetlight",
        "streetlights",
        "street light",
        "street lights",
        "unlit",
        "darkness",
        "dark at night",
    ),
    "Waste": ("garbage", "waste", "overflowing", "bins", "dead animal"),
    "Noise": ("music", "drilling", "amplifiers", "idling with engines"),
    "Road Damage": (
        "road surface",
        "road collapsed",
        "road subsided",
        "road subsidence",
        "footpath",
        "paving",
        "cobblestones",
        "tiles broken",
        "buckled",
        "sinking",
        "cracked",
        "crater",
    ),
    "Heritage Damage": (
        "heritage lamp post",
        "heritage residential building",
        "historic tram road",
        "heritage stone",
        "defaced",
    ),
    "Heat Hazard": (
        "melting",
        "dangerous temperatures",
        "heatwave",
        "temperature",
        "full sun",
        "storing heat",
        "burns",
    ),
    "Drain Blockage": ("drain blocked", "drainage", "stormwater drain"),
}


def _find_evidence(description: str, terms: tuple[str, ...]) -> list[str]:
    """Return matched terms in source order, case-insensitively."""
    matches = []
    for term in terms:
        match = re.search(r"(?i)(?<!\w)" + re.escape(term) + r"(?!\w)", description)
        if match:
            matches.append((match.start(), match.group(0)))
    return [value for _, value in sorted(matches)]


def _invalid_result(complaint_id: object, detail: str) -> dict:
    return {
        "complaint_id": "" if complaint_id is None else str(complaint_id),
        "category": "Other",
        "priority": "Standard",
        "reason": f"The description is {detail}, so the complaint requires review.",
        "flag": "NEEDS_REVIEW",
    }


def classify_complaint(row: dict) -> dict:
    """Classify one complaint into the required five-field output schema."""
    if not isinstance(row, dict):
        return _invalid_result("", "missing or invalid")

    complaint_id = row.get("complaint_id", "")
    description = row.get("description")
    if not isinstance(description, str) or not description.strip():
        return _invalid_result(complaint_id, "missing or invalid")

    description = description.strip()
    category_matches = {
        category: _find_evidence(description, terms)
        for category, terms in CATEGORY_EVIDENCE.items()
    }
    category_matches = {
        category: evidence
        for category, evidence in category_matches.items()
        if evidence
    }

    if len(category_matches) == 1:
        category, evidence = next(iter(category_matches.items()))
        flag = ""
        reason = f'Classified as {category} because the description states "{evidence[0]}".'
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        evidence = [
            item
            for values in category_matches.values()
            for item in values
        ]
        if len(category_matches) > 1:
            cited = '" and "'.join(evidence[:2])
            reason = f'The description contains "{cited}", so the category is ambiguous and requires review.'
        else:
            cited = re.match(r"[A-Za-z0-9]+(?:\s+[A-Za-z0-9]+){0,2}", description)
            evidence_text = cited.group(0) if cited else description.split()[0]
            reason = f'The description mentions "{evidence_text}" but does not identify one allowed complaint category, so it requires review.'

    urgent_evidence = next(
        (
            trigger
            for trigger in URGENT_TRIGGERS
            if re.search(r"(?i)(?<!\w)" + re.escape(trigger) + r"(?!\w)", description)
        ),
        None,
    )
    priority = "Urgent" if urgent_evidence else "Standard"
    if priority == "Urgent":
        reason = f'{reason[:-1]}; urgent because the description states "{urgent_evidence}".'

    return {
        "complaint_id": "" if complaint_id is None else str(complaint_id),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Classify every CSV row and write exactly the required output columns."""
    results = []
    try:
        with open(input_path, "r", newline="", encoding="utf-8") as input_file:
            reader = csv.DictReader(input_file)
            for row in reader:
                try:
                    results.append(classify_complaint(row))
                except (AttributeError, TypeError, ValueError):
                    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
                    results.append(_invalid_result(complaint_id, "malformed"))
    except (OSError, csv.Error):
        results.append(_invalid_result("", "unreadable or malformed"))

    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
