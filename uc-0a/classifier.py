"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

ALLOWED_CATEGORIES = [
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
]

CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole",
        "tyre",
        "blowout",
    ],
    "Flooding": [
        "flood",
        "flooded",
        "flooding",
        "waterlogged",
        "knee-deep",
        "underpass",
        "stranded",
        "inaccessible",
        "rainwater through main road",
    ],
    "Streetlight": [
        "streetlight",
        "street light",
        "lights out",
        "unlit",
        "darkness",
        "dark at night",
        "lamp post",
        "flickering",
        "sparking",
        "substation tripped",
    ],
    "Waste": [
        "waste",
        "garbage",
        "bins",
        "overflow",
        "overflowing",
        "not cleared",
        "dumped",
        "dead animal",
        "piles",
        "health concern",
        "health risk",
    ],
    "Noise": [
        "noise",
        "music",
        "amplifier",
        "amplifiers",
        "drilling",
        "idling",
        "engines on",
        "audible",
        "past midnight",
    ],
    "Road Damage": [
        "road surface",
        "cracked",
        "sinking",
        "subsidence",
        "subsided",
        "collapsed",
        "collapse",
        "crater",
        "buckled",
        "broken",
        "upturned",
        "missing",
        "manhole cover",
        "tiles",
        "paving",
    ],
    "Heritage Damage": [
        "heritage",
        "historic",
        "old city",
        "museum",
        "ancient",
        "step well",
        "cobblestones",
        "defaced",
        "heritage stone",
        "tram road",
    ],
    "Heat Hazard": [
        "heat",
        "heatwave",
        "temperature",
        "melting",
        "unbearable",
        "45",
        "44",
        "52",
        "dangerous temperatures",
        "full sun",
        "burns",
        "unsafe",
    ],
    "Drain Blockage": [
        "drain blocked",
        "drainage blocked",
        "stormwater drain",
        "main drain",
        "drain 100% blocked",
        "sewer blocked",
        "manhole blocked",
    ],
}


def _first_present_text(row: dict, keys: list[str]) -> str:
    for key in keys:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _find_matches(text: str, keywords: list[str]) -> list[str]:
    matches = []
    for kw in keywords:
        if kw in text:
            matches.append(kw)
    return matches


def _build_reason(category: str, priority: str, category_matches: list[str], severity_matches: list[str], flagged: bool) -> str:
    cat_bits = ", ".join(f"'{m}'" for m in category_matches[:2]) if category_matches else "no unique category evidence"
    if severity_matches:
        sev = f"severity word '{severity_matches[0]}'"
        return f"Category set to {category} from {cat_bits}, and priority set to {priority} due to {sev}."
    if flagged:
        return "Category set to Other because description words did not map uniquely to one allowed category, so flag is NEEDS_REVIEW and priority is Standard."
    return f"Category set to {category} from {cat_bits}, and priority set to {priority} because no urgent severity keywords were present."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforces UC-0A schema and ambiguity handling rules from README/skills.
    """
    complaint_id = _first_present_text(row, ["complaint_id", "id", "ticket_id"])
    description = _first_present_text(row, ["description", "complaint", "issue", "details"])

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Category set to Other because no usable description text was provided, so flag is NEEDS_REVIEW and priority is Standard.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    scores = {}
    matched_by_category = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = _find_matches(text, keywords)
        matched_by_category[category] = matches
        scores[category] = len(matches)

    top_score = max(scores.values()) if scores else 0
    winners = [cat for cat, score in scores.items() if score == top_score and score > 0]

    if len(winners) == 1:
        category = winners[0]
        flag = ""
        category_matches = matched_by_category[category]
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        category_matches = []

    severity_matches = _find_matches(text, SEVERITY_KEYWORDS)

    if severity_matches:
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

    reason = _build_reason(
        category=category,
        priority=priority,
        category_matches=category_matches,
        severity_matches=severity_matches,
        flagged=bool(flag),
    )

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in {"Urgent", "Standard", "Low"}:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Continues past row-level errors and writes deterministic output fields.
    """
    results = []

    try:
        with open(input_path, "r", encoding="utf-8", newline="") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV has no header row")

            for idx, row in enumerate(reader, start=1):
                try:
                    results.append(classify_complaint(row))
                except Exception as row_error:
                    complaint_id = ""
                    if isinstance(row, dict):
                        complaint_id = _first_present_text(row, ["complaint_id", "id", "ticket_id"])

                    results.append(
                        {
                            "complaint_id": complaint_id,
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f"Category set to Other because row {idx} could not be processed ({row_error}), so flag is NEEDS_REVIEW and priority is Standard.",
                            "flag": "NEEDS_REVIEW",
                        }
                    )
    except (OSError, csv.Error, ValueError) as file_error:
        raise RuntimeError(f"Failed to read input CSV '{input_path}': {file_error}") from file_error

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow({key: row.get(key, "") for key in fieldnames})
    except OSError as write_error:
        raise RuntimeError(f"Failed to write output CSV '{output_path}': {write_error}") from write_error


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
