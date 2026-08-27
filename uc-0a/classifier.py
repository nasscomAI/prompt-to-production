"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from typing import Dict, List, Optional

ALLOWED_CATEGORIES: List[str] = [
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

SEVERITY_KEYWORDS: List[str] = [
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

CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole", "potholes"]),
    ("Flooding", ["flood", "flooded", "waterlogged", "water logged", "water-logged"]),
    ("Drain Blockage", ["drain", "blocked drain", "blocked drains", "drainage", "sewer", "gutter"]),
    ("Streetlight", ["streetlight", "street lights", "streetlight", "lighting", "lights out", "dark at night", "dark"]),
    ("Waste", ["garbage", "trash", "dumped", "waste", "overflowing bins", "bins", "refuse"]),
    ("Noise", ["noise", "loud music", "music past", "music", "speaker", "sound", "loud"]),
    ("Heritage Damage", ["heritage", "heritage street", "heritage site", "historical", "old city", "monument"]),
    ("Road Damage", ["road surface", "road surface cracked", "cracked", "sinking", "broken road", "manhole", "manhole cover", "footpath tiles", "upturned", "surface cracked"]),
    ("Heat Hazard", ["heat", "heat hazard", "hot", "sunny", "temperature"]),
]

CATEGORY_PRIORITY_ORDER: List[str] = [
    "Pothole",
    "Drain Blockage",
    "Flooding",
    "Streetlight",
    "Noise",
    "Waste",
    "Heritage Damage",
    "Road Damage",
    "Heat Hazard",
]

def _normalize(text: str) -> str:
    return text.strip().lower() if text else ""


def _find_matching_categories(description: str) -> List[str]:
    matches: List[str] = []
    normalized = _normalize(description)
    for category, keywords in CATEGORY_KEYWORDS:
        for keyword in keywords:
            if keyword in normalized:
                matches.append(category)
                break
    return matches


def _choose_category(matches: List[str], description: str) -> str:
    if not matches:
        return "Other"
    for category in CATEGORY_PRIORITY_ORDER:
        if category in matches:
            return category
    return matches[0]


def _contains_severity(description: str) -> bool:
    normalized = _normalize(description)
    for keyword in SEVERITY_KEYWORDS:
        if keyword in normalized:
            return True
    return False


def _determine_priority(category: str, description: str) -> str:
    if _contains_severity(description):
        return "Urgent"
    if category == "Noise":
        return "Low"
    return "Standard"


def _build_reason(category: str, priority: str, description: str) -> str:
    normalized = _normalize(description)
    reason_parts: List[str] = []
    if category != "Other":
        reason_parts.append(f"Category set to {category} based on description")
    else:
        reason_parts.append("Category set to Other because the description is not clearly one of the predefined categories")

    if priority == "Urgent":
        for keyword in SEVERITY_KEYWORDS:
            if keyword in normalized:
                reason_parts.append(f"priority set to Urgent because it mentions '{keyword}'")
                break
    else:
        if category == "Noise":
            reason_parts.append("priority set to Low because the description describes a noise issue without urgent severity keywords")
        else:
            reason_parts.append("priority set to Standard because no urgent severity keyword is present")

    return ". ".join(reason_parts) + "."


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """Classifies a single complaint row into category, priority, reason, and flag."""
    description = row.get("description", "") or ""
    if not description.strip():
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description text, cannot determine category confidently.",
            "flag": "NEEDS_REVIEW",
        }

    matches = _find_matching_categories(description)
    category = _choose_category(matches, description)

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    elif len(set(matches)) > 1 and category == "Other":
        flag = "NEEDS_REVIEW"

    priority = _determine_priority(category, description)
    reason = _build_reason(category, priority, description)

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Reads an input CSV, classifies complaints, and writes results to output CSV."""
    output_fields = ["category", "priority", "reason", "flag"]
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception:
                    result = {
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Classification failed due to invalid input data.",
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
