import argparse
import csv

URGENT_KEYWORDS = [
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

CATEGORY_PATTERNS = [
    ("Heat Hazard", [
        "heatwave",
        "temperature",
        "melting",
        "dangerous temperatures",
        "unbearable",
        "burns",
        "full sun",
        "storing heat",
        "surface bubbling",
        "hot",
    ]),
    ("Drain Blockage", [
        "drain blocked",
        "blocked drain",
        "stormwater drain",
        "main drain",
        "drain completely blocked",
        "blocked storm",
        "drainage blocked",
    ]),
    ("Flooding", [
        "flood",
        "flooded",
        "underpass flooded",
        "waterlogged",
        "water regularly abandoned",
        "rainwater",
        "flood risk",
        "flooding",
    ]),
    ("Pothole", [
        "pothole",
        "potholes",
        "tyre",
        "tire",
        "wheel",
        "sinkhole",
    ]),
    ("Streetlight", [
        "streetlight",
        "street lights",
        "lamp post",
        "lights out",
        "lighting",
        "dark at night",
        "darkness",
    ]),
    ("Waste", [
        "waste",
        "garbage",
        "trash",
        "bins overflowing",
        "overflowing bins",
        "bulk waste",
        "dead animal",
        "animal not removed",
        "dumped on public road",
    ]),
    ("Noise", [
        "noise",
        "music",
        "drilling",
        "amplifier",
        "idling",
        "engine idling",
        "band playing",
        "loud",
        "5am",
        "2am",
    ]),
    ("Heritage Damage", [
        "heritage",
        "heritage zone",
        "heritage precinct",
        "heritage street",
        "historic",
        "heritage building",
        "Tagore Museum",
        "heritage lamp",
        "stone not replaced",
        "historic tram",
        "old city",
    ]),
    ("Road Damage", [
        "subsidence",
        "collapsed",
        "sinking",
        "cracked",
        "buckled",
        "road collapsed",
        "crater",
        "road surface",
        "surface bubbling",
        "road subsidence",
        "deep pothole",
        "footpath broken",
        "road damage",
    ]),
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

def _normalize_text(text: str) -> str:
    return (text or "").lower()


def _contains_any(text: str, keywords):
    normalized = _normalize_text(text)
    for keyword in keywords:
        if keyword in normalized:
            return keyword
    return None


def _determine_category(description: str) -> (str, str):
    normalized_description = _normalize_text(description)
    for category, keywords in CATEGORY_PATTERNS:
        keyword = _contains_any(normalized_description, keywords)
        if keyword:
            return category, keyword
    return "Other", "" 


def _determine_priority(description: str) -> (str, str):
    normalized_description = _normalize_text(description)
    urgent_keyword = _contains_any(normalized_description, URGENT_KEYWORDS)
    if urgent_keyword:
        return "Urgent", urgent_keyword
    return "Standard", ""


def _build_reason(category: str, priority: str, category_hint: str, urgency_hint: str, description: str) -> str:
    if category == "Other":
        phrase = category_hint or description.strip().split(".")[0]
        phrase = phrase[:120].strip()
        return f"Complaint is ambiguous or does not match a UC-0A category; description includes '{phrase}'."

    if urgency_hint:
        return (
            f"Classified as {category} because description mentions '{category_hint}', and priority is Urgent due to '{urgency_hint}'."
        )

    return f"Classified as {category} because description mentions '{category_hint}'."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        row = dict(row or {})

    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    missing_fields = []
    if not complaint_id:
        missing_fields.append("complaint_id")
    if not description:
        missing_fields.append("description")

    if missing_fields:
        reason = (
            f"Missing required field(s): {', '.join(missing_fields)}."
            if missing_fields
            else "Missing required complaint data."
        )
        return {
            "complaint_id": complaint_id or "UNKNOWN",
            "category": "Other",
            "priority": "Low",
            "reason": reason,
            "flag": "NEEDS_REVIEW",
        }

    category, category_hint = _determine_category(description)
    priority, urgency_hint = _determine_priority(description)
    reason = _build_reason(category, priority, category_hint, urgency_hint, description)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

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
    """
    with open(input_path, newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()

        for row_number, row in enumerate(reader, start=1):
            if not row:
                continue

            try:
                result = classify_complaint(row)
            except Exception as exc:
                complaint_id = (row.get("complaint_id") or f"ROW{row_number}").strip() or f"ROW{row_number}"
                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Failed to classify row {row_number}: {exc}",
                    "flag": "NEEDS_REVIEW",
                }

            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
    
