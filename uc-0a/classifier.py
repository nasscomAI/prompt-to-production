import argparse
import csv
import re
from typing import Dict, List

# Allowed schema values (must match README exactly)
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity keywords that MUST trigger Urgent
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

# Keyword mapping for exact allowed categories
CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole",
        "potholes",
    ],
    "Flooding": [
        "flood",
        "flooding",
        "waterlogging",
        "water logged",
        "water-logged",
        "inundated",
    ],
    "Streetlight": [
        "streetlight",
        "street light",
        "streetlights",
        "street lights",
        "lamp post",
        "lamp-post",
        "street lamp",
        "light not working",
        "dark road",
        "dark street",
    ],
    "Waste": [
        "garbage",
        "waste",
        "trash",
        "dump",
        "dumping",
        "litter",
        "overflowing bin",
        "overflowing garbage",
        "overflowing waste",
        "rubbish",
        "bin full",
    ],
    "Noise": [
        "noise",
        "loudspeaker",
        "loud speaker",
        "honking",
        "construction noise",
        "loud music",
        "sound pollution",
    ],
    "Road Damage": [
        "road damage",
        "damaged road",
        "broken road",
        "cracked road",
        "uneven road",
        "road cracked",
        "road broken",
    ],
    "Heritage Damage": [
        "heritage",
        "monument",
        "statue damage",
        "historical wall",
        "fort wall",
        "historic structure",
    ],
    "Heat Hazard": [
        "heat",
        "heatwave",
        "heat wave",
        "extreme heat",
        "heatstroke",
        "hot pavement",
        "no shade",
    ],
    "Drain Blockage": [
        "drain",
        "drainage",
        "blocked drain",
        "clogged drain",
        "manhole",
        "sewage",
        "gutter",
        "drain overflow",
    ],
}


def normalize_text(text: str) -> str:
    """
    Lowercase and normalize whitespace for safer keyword matching.
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_complaint_text(row: Dict[str, str]) -> str:
    """
    Combine all non-empty values from the row into a single searchable text blob.
    This makes the classifier robust to different CSV column names.
    """
    parts: List[str] = []

    for value in row.values():
        if value is None:
            continue
        cleaned = str(value).strip()
        if cleaned:
            parts.append(cleaned)

    return normalize_text(" ".join(parts))


def find_category_matches(text: str) -> Dict[str, List[str]]:
    """
    Return category -> matched keywords for all categories that match.
    """
    matches: Dict[str, List[str]] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        matched_keywords: List[str] = []

        for keyword in keywords:
            if keyword in text:
                matched_keywords.append(keyword)

        if matched_keywords:
            matches[category] = matched_keywords

    return matches


def find_urgent_matches(text: str) -> List[str]:
    """
    Return the urgent keywords found in the complaint text.
    """
    matched: List[str] = []

    for keyword in URGENT_KEYWORDS:
        if keyword in text:
            matched.append(keyword)

    return matched


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    if not complaint_id:
        complaint_id = "UNKNOWN"

    text = build_complaint_text(row)

    # Handle nearly empty / malformed rows safely
    if not text or text == complaint_id.lower():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Insufficient complaint details; category unclear and no urgent keywords found.",
            "flag": "NEEDS_REVIEW",
        }

    category_matches = find_category_matches(text)
    urgent_matches = find_urgent_matches(text)

    flag = ""

    # Decide category
    if not category_matches:
        category = "Other"
        flag = "NEEDS_REVIEW"
        category_reason = "no clear category keywords found"
    elif len(category_matches) == 1:
        category = next(iter(category_matches))

        matched_reasons_all = category_matches[category]
        matched_reasons: List[str] = []

        for item in matched_reasons_all:
            if len(matched_reasons) < 3:
                matched_reasons.append(item)
            else:
                break

        category_reason = f"matched {', '.join(matched_reasons)}"
    else:
        # Multiple category signals => ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        matched_categories = list(category_matches.keys())
        category_reason = f"multiple category signals: {', '.join(matched_categories)}"

    # Decide priority
    if urgent_matches:
        priority = "Urgent"

        top_urgent_matches: List[str] = []

        for item in urgent_matches:
            if len(top_urgent_matches) < 3:
                top_urgent_matches.append(item)
            else:
                break

        urgent_reason = f"urgent keywords found: {', '.join(top_urgent_matches)}"
    else:
        # If the complaint is unclear/weak-signal, use Low; otherwise Standard
        if category == "Other":
            priority = "Low"
        else:
            priority = "Standard"
        urgent_reason = "no urgent keywords found"

    reason = f"Category based on {category_reason}; priority based on {urgent_reason}."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for index, row in enumerate(reader, start=1):
            try:
                if row is None:
                    result = {
                        "complaint_id": f"ROW-{index}",
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Malformed row encountered; category unclear and no urgent keywords found.",
                        "flag": "NEEDS_REVIEW",
                    }
                else:
                    result = classify_complaint(row)

                writer.writerow(result)

            except Exception as exc:
                fallback_id = ""
                if row and isinstance(row, dict):
                    fallback_id = str(row.get("complaint_id", "")).strip()

                if not fallback_id:
                    fallback_id = f"ROW-{index}"

                writer.writerow(
                    {
                        "complaint_id": fallback_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Row processing failed ({type(exc).__name__}); sent for review.",
                        "flag": "NEEDS_REVIEW",
                    }
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")