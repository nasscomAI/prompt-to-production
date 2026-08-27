"""
UC-0A — Complaint Classifier

Deterministic classifier for the approved civic complaint taxonomy.
"""
import argparse
import csv
import re
from pathlib import Path


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
OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]
SEVERITY_RE = re.compile(
    r"\b(injur\w*|child\w*|school\w*|hospital\w*|ambulance\w*|fire\w*|hazard\w*|fell|collaps\w*)\b",
    re.IGNORECASE,
)
LINE_PREFIX_RE = re.compile(r"^\s*\d+\|")


CATEGORY_RULES = [
    (
        "Heat Hazard",
        (
            "heat",
            "heatwave",
            "temperature",
            "44",
            "45",
            "52",
            "melting",
            "burn",
            "full sun",
            "dangerous temperatures",
            "unbearable",
        ),
    ),
    ("Pothole", ("pothole", "potholes")),
    ("Drain Blockage", ("drain blocked", "drain completely blocked", "blocked with", "main drain blocked", "manhole")),
    ("Flooding", ("flood", "flooded", "floods", "water", "rainwater", "knee-deep", "stormwater")),
    (
        "Streetlight",
        (
            "streetlight",
            "streetlights",
            "lights out",
            "lamp post",
            "unlit",
            "darkness",
            "dark at night",
            "substation",
        ),
    ),
    ("Waste", ("garbage", "waste", "bins", "dead animal", "not cleared", "piles")),
    ("Noise", ("music", "drilling", "amplifier", "amplifiers", "band", "idling", "engines on")),
    (
        "Heritage Damage",
        (
            "heritage lamp",
            "historic tram",
            "cobblestone",
            "heritage building",
            "heritage stone",
            "ancient step",
            "defaced",
            "not restored",
            "not replaced",
            "billboard",
        ),
    ),
    (
        "Road Damage",
        (
            "road surface",
            "road collapsed",
            "cracked",
            "sinking",
            "subsidence",
            "buckled",
            "broken",
            "upturned",
            "footpath",
            "tiles",
            "crater",
            "bridge approach",
            "surface bubbling",
        ),
    ),
]


def _clean_cell(value) -> str:
    """Normalize CSV cells and remove accidental copied line-number prefixes."""
    if value is None:
        return ""
    return LINE_PREFIX_RE.sub("", str(value)).strip()


def _contains_any(text: str, keywords: tuple[str, ...]) -> str:
    for keyword in keywords:
        if keyword in text:
            return keyword
    return ""


def _evidence_phrase(description: str, matched_keyword: str) -> str:
    if not description:
        return "missing description"

    if matched_keyword:
        match = re.search(re.escape(matched_keyword), description, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 30)
            end = min(len(description), match.end() + 45)
            return description[start:end].strip(" .,")

    return description[:80].strip(" .,")


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    clean_row = {str(key or "").strip(): _clean_cell(value) for key, value in (row or {}).items()}
    complaint_id = clean_row.get("complaint_id", "")
    description = clean_row.get("description", "")

    if not complaint_id or not description:
        missing = "complaint_id" if not complaint_id else "description"
        return {
            "complaint_id": complaint_id or "UNKNOWN",
            "category": "Other",
            "priority": "Low",
            "reason": f"Needs review because {missing} is missing from the input row.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    matched_keyword = ""
    category = "Other"

    for candidate, keywords in CATEGORY_RULES:
        matched_keyword = _contains_any(text, keywords)
        if matched_keyword:
            category = candidate
            break

    if category not in ALLOWED_CATEGORIES:
        category = "Other"

    severity_match = SEVERITY_RE.search(description)
    priority = "Urgent" if severity_match else "Standard"
    flag = "" if category != "Other" else "NEEDS_REVIEW"
    evidence = _evidence_phrase(description, matched_keyword or (severity_match.group(0) if severity_match else ""))

    if category == "Other":
        reason = f"Needs review because the description '{evidence}' does not clearly match the approved categories."
    else:
        reason = f"Classified as {category} because the description says '{evidence}'."

    if severity_match:
        reason = reason.rstrip(".") + f"; priority is Urgent due to '{severity_match.group(0)}'."

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
    Flags nulls, does not crash on bad rows, and produces output for readable rows.
    """
    results = []

    with open(input_path, newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        for row_number, row in enumerate(reader, start=2):
            try:
                results.append(classify_complaint(row))
            except Exception as exc:
                complaint_id = _clean_cell((row or {}).get("complaint_id")) or f"ROW-{row_number}"
                results.append(
                    {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Needs review because row {row_number} could not be classified: {exc}.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    output_file_path = Path(output_path)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    with output_file_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
