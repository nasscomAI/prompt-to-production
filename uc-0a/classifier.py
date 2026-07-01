"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from typing import Dict, List, Optional

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
    "Pothole": ["pothole", "sinkhole", "road crater"],
    "Flooding": ["flood", "flooded", "waterlogged", "knee-deep", "underpass flooded", "bridge approach floods", "commuters stranded"],
    "Streetlight": ["streetlight", "lights out", "dark at night", "flickering", "sparking", "light out"],
    "Waste": ["garbage", "bins", "dumped", "bulk waste", "waste", "trash", "refuse", "dead animal"],
    "Noise": ["music", "noise", "loud", "midnight", "sound"],
    "Road Damage": ["cracked", "sinking", "road surface", "tiles broken", "upturned", "manhole cover missing", "footpath tiles"],
    "Heritage Damage": ["heritage", "heritage street", "historic", "old city"],
    "Heat Hazard": ["heat", "temperature", "scorching", "heat hazard"],
    "Drain Blockage": ["drain blocked", "blocked drain", "drain blocked", "drain", "sewage"],
}

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _find_first_keyword(description: str, keywords: List[str]) -> Optional[str]:
    for keyword in keywords:
        if keyword in description:
            return keyword
    return None


def classify_category(description: str) -> (str, bool):
    normalized = _normalize_text(description)
    for category, keywords in CATEGORY_KEYWORDS.items():
        citation = _find_first_keyword(normalized, keywords)
        if citation:
            return category, False

    if "manhole" in normalized or "cover missing" in normalized:
        return "Road Damage", False

    return "Other", True


def determine_priority(description: str) -> str:
    normalized = _normalize_text(description)
    if _find_first_keyword(normalized, SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


def build_reason(description: str, category: str, priority: str) -> str:
    normalized = _normalize_text(description)
    if not normalized:
        return "No description available for classification."

    keyword = _find_first_keyword(normalized, CATEGORY_KEYWORDS.get(category, []))
    if not keyword:
        keyword = _find_first_keyword(normalized, SEVERITY_KEYWORDS)
    if keyword:
        if priority == "Urgent" and keyword in SEVERITY_KEYWORDS:
            return f"Urgent because description mentions \"{keyword}\" and fits {category}."
        return f"Classified as {category} because description mentions \"{keyword}\"."

    first_sentence = description.split(".")[0].strip()
    return f"Classified as {category} based on description: {first_sentence}."


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided. Needs review.",
            "flag": "NEEDS_REVIEW",
        }

    category, ambiguous = classify_category(description)
    priority = determine_priority(description)
    reason = build_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        for index, row in enumerate(reader, start=1):
            try:
                output_row = classify_complaint(row)
            except Exception as error:
                output_row = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed for row {index}: {error}",
                    "flag": "NEEDS_REVIEW",
                }
            rows.append(output_row)

    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
