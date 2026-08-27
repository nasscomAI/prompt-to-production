"""
UC-0A — Complaint Classifier
A lightweight rule-based implementation of the complaint classification workflow.
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

CATEGORY_RULES: List[Tuple[List[str], str]] = [
    (["pothole"], "Pothole"),
    (["flood", "flooded", "waterlogged", "inundat", "rain"], "Flooding"),
    (["drain", "blocked", "blockage", "manhole"], "Drain Blockage"),
    (["streetlight", "street light", "light", "lamp", "sparking", "flickering", "electrical"], "Streetlight"),
    (["waste", "garbage", "trash", "bin", "bins", "dump", "animal", "smell"], "Waste"),
    (["noise", "music", "loud", "sound"], "Noise"),
    (["road", "surface", "crack", "cracked", "pavement", "tiles", "footpath", "broken", "sinking"], "Road Damage"),
    (["heritage"], "Heritage Damage"),
    (["heat", "hot", "temperature", "sun"], "Heat Hazard"),
]


def _extract_description(row: dict) -> str:
    for key in ["description", "complaint", "text", "issue"]:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _match_category(description: str) -> Tuple[str, bool]:
    lowered = description.lower()
    for keywords, category in CATEGORY_RULES:
        if any(keyword in lowered for keyword in keywords):
            return category, False

    if not description.strip():
        return "Other", True

    return "Other", True


def _match_priority(description: str) -> str:
    lowered = description.lower()
    if any(keyword in lowered for keyword in URGENCY_KEYWORDS):
        return "Urgent"
    if "noise" in lowered or "music" in lowered:
        return "Low"
    return "Standard"


def _build_reason(description: str, category: str) -> str:
    if not description.strip():
        return "No description was provided to justify a category."

    if category == "Other":
        return "The description is too ambiguous to justify a specific category."

    evidence = []
    lowered = description.lower()
    for keyword in ["pothole", "flood", "streetlight", "waste", "noise", "road", "heritage", "heat", "drain", "block", "hazard", "injury", "child", "school", "hospital", "ambulance", "fire", "fell", "collapse"]:
        if keyword in lowered:
            evidence.append(keyword)
            break

    if evidence:
        return f"The description mentions '{evidence[0]}' as supporting evidence for {category.lower()}."
    return f"The description supports {category.lower()} based on its wording."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag.
    """
    description = _extract_description(row)
    complaint_id = row.get("complaint_id") or row.get("id") or ""

    try:
        category, needs_review = _match_category(description)
        priority = _match_priority(description)
        reason = _build_reason(description, category)
        flag = "NEEDS_REVIEW" if needs_review else ""
    except Exception:
        category = "Other"
        priority = "Standard"
        reason = "The complaint could not be classified reliably from the provided text."
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
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id") or row.get("id") or "",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "The complaint could not be classified reliably from the provided text.",
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
