"""
UC-0A — Complaint Classifier
Starter file. Build this using your RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

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

URGENCY_KEYWORDS = [
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

CATEGORY_RULES = [
    ("Drain Blockage", ["drain", "blocked", "blocked drain", "drainage", "sewer", "gully", "storm drain"]),
    ("Flooding", ["flood", "flooded", "waterlogged", "underpass flooded", "knee-deep", "in water", "standing in water"]),
    ("Pothole", ["pothole", "potholes"]),
    ("Streetlight", ["streetlight", "street lights", "streetlight flickering", "light out", "lights out", "street light", "streetlights"]),
    ("Heritage Damage", ["heritage", "heritage street", "historical", "old city", "heritage building", "monument"]),
    ("Waste", ["garbage", "waste", "trash", "dumped", "dumping", "bins", "bin", "rubbish", "dead animal"]),
    ("Noise", ["noise", "music past midnight", "playing music", "loud", "late night"]),
    ("Road Damage", ["road surface", "cracked", "sinking", "broken", "footpath", "tiles broken", "upturned", "road damage", "surface cracked", "manhole cover missing"]),
    ("Heat Hazard", ["heat", "hot", "heat hazard", "heatwave", "smoke"]),
]


def _find_keywords(text: str, keywords: list[str]) -> list[str]:
    matches = []
    for keyword in keywords:
        if re.search(r"\b" + re.escape(keyword) + r"\b", text, flags=re.IGNORECASE):
            matches.append(keyword)
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag, location, ward
    """
    complaint_id = str(row.get("complaint_id", "")).strip() or "unknown"
    location = str(row.get("location", "")).strip()
    ward = str(row.get("ward", "")).strip()
    description = str(row.get("description", "")).strip()
    description_lower = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing, so category is set to Other and flag is NEEDS_REVIEW.",
            "flag": "NEEDS_REVIEW",
            "location": location,
            "ward": ward,
        }

    category = "Other"
    evidence = []

    for category_name, keywords in CATEGORY_RULES:
        found = _find_keywords(description_lower, keywords)
        if found:
            category = category_name
            evidence = found
            break

    priority_terms = _find_keywords(description_lower, URGENCY_KEYWORDS)
    priority = "Urgent" if priority_terms else "Standard"
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    if evidence:
        evidence_text = " and ".join(f'"{item}"' for item in evidence[:2])
        reason = f"Classified as {category} because the description contains {evidence_text}."
    else:
        reason = (
            "Description did not match a precise category keyword, so the complaint is classified as Other."
            if category == "Other"
            else f"Classified as {category} based on the complaint description."
        )

    if priority == "Urgent":
        urgent_text = " and ".join(f'"{item}"' for item in priority_terms[:2])
        reason = f"Classified as {category} and Urgent because the description contains {urgent_text}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
        "location": location,
        "ward": ward,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        input_fields = reader.fieldnames or []
        rows = list(reader)

    extra_fields = ["category", "priority", "reason", "flag"]
    output_fields = input_fields + [f for f in extra_fields if f not in input_fields]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row_number, row in enumerate(rows, start=1):
            try:
                result = classify_complaint(row)
                output_row = {**row, **result}
                writer.writerow(output_row)
            except Exception:
                complaint_id = str(row.get("complaint_id", "")).strip() or f"row_{row_number}"
                output_row = {**row}
                output_row.update({
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Low",
                    "reason": (
                        "Failed to classify this row due to malformed input. "
                        "Set to Other and flagged for review."
                    ),
                    "flag": "NEEDS_REVIEW",
                })
                writer.writerow(output_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
