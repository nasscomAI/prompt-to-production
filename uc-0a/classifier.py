import argparse
import csv
import re
from pathlib import Path

CATEGORIES = (
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
)

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

LOW_PRIORITY_KEYWORDS = (
    "minor",
    "slight",
    "cosmetic",
    "small",
    "occasionally",
)

CATEGORY_KEYWORDS = {
    "Pothole": (
        "pothole",
        "hole in the road",
        "road hole",
    ),
    "Flooding": (
        "flood",
        "flooded",
        "flooding",
        "waterlogging",
        "water logged",
        "waterlogged",
    ),
    "Streetlight": (
        "streetlight",
        "street light",
        "lamp post",
        "lamp is out",
        "light is out",
        "no light",
        "dark street",
    ),
    "Waste": (
        "garbage",
        "trash",
        "rubbish",
        "waste",
        "litter",
        "dumping",
        "dumped",
        "uncleared bins",
    ),
    "Noise": (
        "noise",
        "noisy",
        "loud",
        "sound pollution",
        "music",
        "disturbance",
    ),
    "Road Damage": (
        "road damage",
        "damaged road",
        "broken road",
        "cracked road",
        "road crack",
        "road surface",
        "road is broken",
    ),
    "Heritage Damage": (
        "heritage",
        "monument",
        "historical",
        "historic",
        "temple",
        "fort",
        "old building",
    ),
    "Heat Hazard": (
        "heat",
        "heatwave",
        "hot surface",
        "extreme temperature",
        "scorching",
    ),
    "Drain Blockage": (
        "drain",
        "blocked drain",
        "drain blockage",
        "clogged drain",
        "sewer",
        "gutter",
    ),
}


def classify_complaint(row: dict) -> dict:
    """Classify one complaint row into the required output schema."""
    if not isinstance(row, dict):
        row = {}
    complaint_id = row.get("complaint_id", row.get("id", ""))
    description = _description_from_row(row)
    normalised = _normalise(description)
    urgent_matches = _find_matches(normalised, URGENT_KEYWORDS)
    category_matches = {
        category: _find_matches(normalised, keywords)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    matched_categories = [
        category for category, matches in category_matches.items() if matches
    ]
    if len(matched_categories) == 1:
        category = matched_categories[0]
        evidence = category_matches[category][0]
        flag = ""
        reason = _sentence(
            f"Classified as {category} because the description mentions "
            f'"{evidence}"'
        )
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if not description:
            reason = "Description is missing, so the category cannot be determined."
        elif len(matched_categories) > 1:
            evidence = ", ".join(matched_categories)
            reason = _sentence(
                f'The description matches multiple categories: "{evidence}"'
            )
        else:
            reason = _sentence(
                f"No allowed category is clearly supported by the description: "
                f'"{description}"'
            )
    if urgent_matches:
        priority = "Urgent"
        priority_reason = urgent_matches[0]
    elif _find_matches(normalised, LOW_PRIORITY_KEYWORDS):
        priority = "Low"
        priority_reason = _find_matches(normalised, LOW_PRIORITY_KEYWORDS)[0]
    else:
        priority = "Standard"
        priority_reason = None
    if priority_reason:
        reason = _sentence(
            f"{reason[:-1]}; priority is {priority} because the description "
            f'mentions "{priority_reason}"'
        )
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _description_from_row(row: dict) -> str:
    for key in ("description", "complaint", "details", "text"):
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _find_matches(text: str, keywords: tuple[str, ...]) -> list[str]:
    return [keyword for keyword in keywords if keyword in text]


def _sentence(text: str) -> str:
    text = " ".join(text.split()).strip()
    if not text:
        return "Description is missing."
    return text if text.endswith((".", "!", "?")) else f"{text}."


def batch_classify(input_path: str, output_path: str):
    """Classify every input row and write one output row per input row."""
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            for row_number, row in enumerate(reader, start=2):
                if row is None:
                    row = {}
                try:
                    result = classify_complaint(row)
                    if not result["complaint_id"]:
                        result["complaint_id"] = row_number
                except Exception as exc:
                    result = {
                        "complaint_id": row.get("complaint_id", row_number),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": _sentence(f"Row could not be classified: {exc}"),
                        "flag": "NEEDS_REVIEW",
                    }
                results.append(result)
    except (OSError, csv.Error) as exc:
        results.append(
            {
                "complaint_id": "",
                "category": "Other",
                "priority": "Standard",
                "reason": _sentence(f"Input file could not be read: {exc}"),
                "flag": "NEEDS_REVIEW",
            }
        )
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
