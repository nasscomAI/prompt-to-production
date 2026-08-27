"""
UC-0A — Complaint Classifier
Rule-based implementation aligned to the UC-0A schema in the project README.
"""
import argparse
import csv
import re
from typing import Any, Dict, List, Optional

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

CATEGORY_RULES: List[tuple[str, List[str]]] = [
    ("Heritage Damage", ["heritage", "ancient", "historic", "old city", "step well"]),
    ("Heat Hazard", ["heat", "hot", "temperature", "sun", "heatwave", "burn", "burns", "melting"]),
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "flooded", "flooding", "waterlogging", "waterlogged", "inundated", "underpass"]),
    ("Drain Blockage", ["drain", "drainage", "blocked", "blockage", "clog", "clogged", "manhole", "sewer", "sewage"]),
    ("Streetlight", ["streetlight", "streetlights", "lights out", "light out", "lights", "light", "flickering", "sparking", "dark"]),
    ("Waste", ["waste", "garbage", "bin", "bins", "dumped", "animal", "trash"]),
    ("Noise", ["noise", "music", "loud", "midnight"]),
    ("Road Damage", ["crack", "cracked", "cracks", "sinking", "subsidence", "footpath", "tiles", "upturned", "bubbling", "surface"]),
]


def _extract_text(row: Dict[str, Any]) -> str:
    if not isinstance(row, dict):
        return ""
    for key in ("description", "Description", "complaint_description", "complaint"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for key in ("location", "Location", "ward", "Ward"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _match_categories(description: str) -> List[str]:
    if not description:
        return []

    lowered = description.lower()
    matched = []
    for category, keywords in CATEGORY_RULES:
        if any(keyword in lowered for keyword in keywords):
            matched.append(category)
    return matched


def _choose_category(description: str) -> tuple[str, List[str]]:
    matched = _match_categories(description)
    if len(matched) > 1:
        return "Other", matched
    if len(matched) == 1:
        return matched[0], matched
    return "Other", []


def _choose_priority(description: str, category: str) -> tuple[str, Optional[str]]:
    lowered = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if keyword in lowered:
            return "Urgent", keyword

    if not description:
        return "Low", None

    if category in {"Noise"}:
        return "Low", None
    return "Standard", None


def _build_reason(description: str, category: str, priority: str, urgency_keyword: Optional[str], matched_categories: List[str]) -> str:
    if not description:
        return "The complaint text is blank, so it is marked for review."

    if len(matched_categories) > 1:
        categories_text = ", ".join(matched_categories)
        if urgency_keyword:
            return f"The description contains signals for multiple categories ({categories_text}), so it is marked NEEDS_REVIEW; priority is Urgent because the severity keyword '{urgency_keyword}' appears."
        return f"The description contains signals for multiple categories ({categories_text}), so it is marked NEEDS_REVIEW."

    if not matched_categories:
        words = re.findall(r"[A-Za-z]+", description)
        if len(words) >= 2:
            return f"The description mentions '{words[0]}' and '{words[1]}' but does not clearly fit a standard category."
        return f"The description mentions '{description.strip()}' but does not clearly fit a standard category."

    matched_category = matched_categories[0]
    keyword = None
    lowered = description.lower()
    for candidate in CATEGORY_RULES:
        if candidate[0] == matched_category:
            for term in candidate[1]:
                if term in lowered:
                    keyword = term
                    break
            break

    if priority == "Urgent" and urgency_keyword:
        return f"The description mentions '{keyword or matched_category.lower()}' and matches the {category} category; priority is Urgent because the severity keyword '{urgency_keyword}' appears."
    return f"The description mentions '{keyword or matched_category.lower()}' and matches the {category} category."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = ""
    if isinstance(row, dict):
        complaint_id = row.get("complaint_id") or row.get("complaintId") or ""

    description = _extract_text(row)
    category, matched_categories = _choose_category(description)
    priority, urgency_keyword = _choose_priority(description, category)
    reason = _build_reason(description, category, priority, urgency_keyword, matched_categories)
    flag = "NEEDS_REVIEW" if category == "Other" or len(matched_categories) > 1 or not description else ""

    return {
        "complaint_id": complaint_id if complaint_id is not None else "",
        "category": category if category in ALLOWED_CATEGORIES else "Other",
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, "r", newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            with open(output_path, "w", newline="", encoding="utf-8") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in reader:
                    try:
                        result = classify_complaint(row)
                    except Exception:
                        result = {
                            "complaint_id": (row.get("complaint_id") if isinstance(row, dict) else "") or "",
                            "category": "Other",
                            "priority": "Low",
                            "reason": "The row could not be classified safely, so it was marked for review.",
                            "flag": "NEEDS_REVIEW",
                        }
                    writer.writerow(result)
    except FileNotFoundError:
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerow({
                "complaint_id": "",
                "category": "Other",
                "priority": "Low",
                "reason": "Input file was not found, so the row was marked for review.",
                "flag": "NEEDS_REVIEW",
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
