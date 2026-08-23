"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re


ALLOWED_CATEGORIES = (
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
ALLOWED_PRIORITIES = ("Urgent", "Standard", "Low")
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

_CATEGORY_RULES = (
    ("Heritage Damage", ("heritage damage", "historic damage", "damaged monument", "damaged listed building")),
    ("Heat Hazard", ("heatwave", "heat wave", "extreme heat", "heat hazard")),
    ("Drain Blockage", ("drain blocked", "blocked drain", "drain blockage", "clogged drain", "manhole")),
    ("Streetlight", ("streetlight", "street light", "lamp post", "lights out", "lighting")),
    ("Flooding", ("flood", "waterlogged", "underpass flooded", "standing water")),
    ("Pothole", ("pothole",)),
    ("Road Damage", ("road surface", "road damaged", "road damage", "cracked road", "footpath", "road sinking")),
    ("Waste", ("garbage", "waste", "rubbish", "dumped", "dead animal", "litter")),
    ("Noise", ("noise", "music", "loud", "sound pollution")),
)


def _contains_keyword(text: str, keyword: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", text, re.IGNORECASE) is not None


def _evidence(text: str, keywords: tuple[str, ...]) -> str | None:
    for keyword in keywords:
        match = re.search(re.escape(keyword), text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Invalid or ambiguous rows are returned as Other/NEEDS_REVIEW rather than
    preventing the rest of a batch from being written.
    """
    complaint_id_value = row.get("complaint_id", "")
    description_value = row.get("description", "")
    complaint_id = complaint_id_value.strip() if isinstance(complaint_id_value, str) else ""
    description = description_value.strip() if isinstance(description_value, str) else ""
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description was provided for classification.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.casefold()
    matches = []
    for category, keywords in _CATEGORY_RULES:
        matched = _evidence(text, keywords)
        if matched:
            matches.append((category, matched))

    severity = next((keyword for keyword in SEVERITY_KEYWORDS if _contains_keyword(text, keyword)), None)
    priority = "Urgent" if severity else "Standard"
    if len(matches) == 1:
        category, matched = matches[0]
        reason = f"Classified as {category} because the description mentions '{matched}'."
        flag = ""
    elif not matches:
        category = "Other"
        reason = "Classified as Other because no allowed category term appears in the description."
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        matched_terms = ", ".join(f"'{match[1]}'" for match in matches)
        reason = f"The description mentions {matched_terms}, which match multiple categories and make the category ambiguous."
        flag = "NEEDS_REVIEW"

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
    
    Bad rows are represented in the output and do not stop later rows.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(input_path, newline="", encoding="utf-8-sig") as input_file:
        rows = csv.DictReader(input_file)
        with open(output_path, "w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                try:
                    result = classify_complaint(row)
                except (AttributeError, TypeError, ValueError) as error:
                    result = {
                        "complaint_id": str(row.get("complaint_id", "")).strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification failed for this row: {error}.",
                        "flag": "NEEDS_REVIEW",
                    }
                writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
