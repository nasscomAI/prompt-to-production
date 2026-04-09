"""UC-0A Complaint Classifier."""

import argparse
import csv
import re


ALLOWED_OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]
SEVERITY_KEYWORDS = (
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


def _normalize(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _contains_any(text: str, patterns: tuple[str, ...]) -> tuple[bool, str]:
    for pattern in patterns:
        if pattern in text:
            return True, pattern
    return False, ""


def _priority_from_description(description: str) -> str:
    return "Urgent" if any(keyword in description for keyword in SEVERITY_KEYWORDS) else "Standard"


def _classify_by_description(description: str) -> tuple[str, str, bool]:
    text = _normalize(description)
    if not text:
        return "Other", "Description is missing, so the complaint cannot be classified from text alone.", True

    flood_patterns = (
        "underpass flooded",
        "underpass floods",
        "flooded",
        "floods",
        "flooding",
        "waterlogged",
        "rainwater through",
        "rainwater",
        "water on road",
    )
    road_damage_patterns = (
        "road collapsed",
        "road collapsed partially",
        "collapsed road",
        "road caved",
        "road sunk",
        "sinkhole",
        "crater",
        "road damage",
    )
    pothole_patterns = (
        "pothole",
        "potholes",
    )
    drain_blockage_patterns = (
        "drain completely blocked",
        "stormwater drain blocked",
        "drain blocked",
        "blocked drain",
        "blocked with construction debris",
        "drain blockage",
        "blocked sewer",
        "sewer blocked",
        "blocked with",
    )
    waste_patterns = (
        "garbage overflow",
        "waste not cleared",
        "garbage",
        "waste",
        "litter",
        "rubbish",
        "trash",
        "overflow",
        "not cleared",
    )
    noise_patterns = (
        "construction drilling",
        "drilling",
        "idling",
        "engines on",
        "noise",
        "loud",
        "honking",
    )
    streetlight_patterns = (
        "streetlight",
        "street light",
        "lamp post",
        "lights out",
    )
    heat_patterns = (
        "heat hazard",
        "heatwave",
        "heat wave",
        "extreme heat",
        "no shade",
        "scorching",
        "dehydration",
    )
    heritage_damage_patterns = (
        "heritage structure",
        "heritage damage",
        "monument",
        "charminar",
        "heritage building",
        "vandal",
        "damage to heritage",
        "heritage site",
    )

    checks = [
        ("Flooding", flood_patterns, "Description contains flood-related words"),
        ("Road Damage", road_damage_patterns, "Description shows road collapse or a crater"),
        ("Pothole", pothole_patterns, "Description mentions potholes"),
        ("Drain Blockage", drain_blockage_patterns, "Description says the drain is blocked"),
        ("Waste", waste_patterns, "Description mentions waste or garbage overflow"),
        ("Noise", noise_patterns, "Description mentions drilling, idling, or other noise"),
        ("Streetlight", streetlight_patterns, "Description mentions a streetlight problem"),
        ("Heat Hazard", heat_patterns, "Description mentions heat exposure or heat hazard"),
        ("Heritage Damage", heritage_damage_patterns, "Description mentions heritage damage"),
    ]

    for category, patterns, reason_prefix in checks:
        found, evidence = _contains_any(text, patterns)
        if found:
            reason = f"{reason_prefix} with '{evidence}', so it is classified as {category}."
            return category, reason, False

    return "Other", "Description does not match the allowed categories, so it needs review.", True


def classify_complaint(row: dict) -> dict:
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = row.get("description", "")

    category, reason, needs_review = _classify_by_description(description)
    priority = _priority_from_description(_normalize(description))
    flag = "NEEDS_REVIEW" if needs_review else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8-sig") as input_file, open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=ALLOWED_OUTPUT_FIELDS)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # noqa: BLE001
                result = {
                    "complaint_id": str(row.get("complaint_id", "")).strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be classified safely because {exc}.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow({field: result.get(field, "") for field in ALLOWED_OUTPUT_FIELDS})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
