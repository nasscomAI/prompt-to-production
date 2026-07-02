"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import os
import re
from typing import Dict, List, Tuple

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

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "water", "waterlogging", "waterlogged", "underpass", "rain"],
    "Streetlight": ["streetlight", "street light", "streetlights", "lights out", "light out", "flickering", "sparking", "dark", "electrical hazard"],
    "Waste": ["garbage", "waste", "trash", "dumped", "bins", "bin", "overflowing", "smell"],
    "Noise": ["noise", "music", "loud", "sound", "midnight", "nuisance"],
    "Road Damage": ["road", "road surface", "cracked", "surface", "footpath", "tiles", "broken", "upturned", "sinking", "utility"],
    "Heritage Damage": ["heritage", "historic", "monument", "old city"],
    "Heat Hazard": ["heat", "hot", "temperature", "sun", "shade", "heatwave"],
    "Drain Blockage": ["drain", "blocked", "blockage", "clog", "clogged", "sewer", "manhole"],
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _contains_keyword(text: str, keyword: str) -> bool:
    return re.search(rf"\b{re.escape(keyword)}s?\b", text) is not None


def _score_categories(text: str) -> List[Tuple[str, int, List[str]]]:
    normalized = _normalize(text)
    scores: List[Tuple[str, int, List[str]]] = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [keyword for keyword in keywords if keyword in normalized]
        scores.append((category, len(matched), matched))
    return scores


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row or {}).get("complaint_id", "") or ""
    description = (row or {}).get("description", "") or ""
    normalized_description = _normalize(description)

    if not normalized_description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is missing, so the category cannot be determined.",
            "flag": "NEEDS_REVIEW",
        }

    scored_categories = _score_categories(description)
    scored_categories.sort(key=lambda item: item[1], reverse=True)
    top_category, top_score, top_matches = scored_categories[0]
    second_category, second_score, _ = scored_categories[1]

    if top_score == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif top_score == second_score and second_score > 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = top_category if top_category in ALLOWED_CATEGORIES else "Other"
        flag = ""

    is_urgent = any(_contains_keyword(normalized_description, keyword) for keyword in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else ("Low" if category in {"Noise", "Waste"} else "Standard")

    # Build a reason string that cites description tokens and explains category + priority
    if top_score == 0:
        reason = "The description does not clearly match any supported category."
    elif top_score == second_score and second_score > 0:
        reason = (
            f"The description mentions multiple signals; it is ambiguous between categories,"
            " so returning 'Other' and flagging for review."
        )
    else:
        if top_matches:
            matched_keywords = ", ".join(f"'{keyword}'" for keyword in top_matches[:3])
        else:
            matched_keywords = "relevant keywords"
        priority_reason = "because severity keywords were found." if is_urgent else "because no severity keywords were found."
        reason = (
            f"The description contains {matched_keywords}, so the category is '{category}'"
            f" and the priority is '{priority}' {priority_reason}"
        )
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
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        input_fieldnames = reader.fieldnames or []

    output_fieldnames = list(input_fieldnames) + ["category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()

        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": (row or {}).get("complaint_id", "") or "",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "The row could not be processed correctly.",
                    "flag": "NEEDS_REVIEW",
                }
            # Merge original row with classification results so output preserves all input columns
            output_row = dict(row)
            output_row.update(result)
            writer.writerow(output_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
