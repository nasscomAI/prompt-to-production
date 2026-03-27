"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import re
from typing import Optional


VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole", "pot hole", "hole in road", "hole in the road",
        "crater in road", "crater on road", "road hole",
    ],
    "Flooding": [
        "flood", "flooding", "waterlogged", "water logging",
        "water accumulation", "water overflow", "inundat",
        "submerged", "ankle deep water", "knee deep water",
    ],
    "Streetlight": [
        "streetlight", "street light", "lamp post", "lampost",
        "light not working", "light out", "broken light",
        "no light", "dark street", "pole light", "street lamp",
    ],
    "Waste": [
        "garbage", "trash", "waste", "rubbish", "litter",
        "dump", "refuse", "debris", "rubble", "pile of waste",
        "garbage dump", "trash pile", "waste pile",
    ],
    "Noise": [
        "noise", "loud music", "loudspeaker", "decibel",
        "sound pollution", "noisy", "drilling noise",
        "construction noise", "horn", "blaring",
    ],
    "Road Damage": [
        "road damage", "damaged road", "cracked road", "road crack",
        "broken road", "uneven road", "road surface", "worn out road",
        "bumpy road", "road deterioration", "road worn",
    ],
    "Heritage Damage": [
        "heritage", "monument", "historic", "old building damage",
        "heritage site", "ancient", "colonial", "fort damage",
        "temple damage", "museum", "statue damage",
    ],
    "Heat Hazard": [
        "heat", "heatwave", "extreme heat", "scorching",
        "heat stroke", "burning road", "melting road",
        "tar melting", "temperature",
    ],
    "Drain Blockage": [
        "drain", "sewer", "blocked drain", "clogged drain",
        "gutter", "waterlogging", "storm drain", "sewage",
        "overflowing drain", "drainage", "pipe block",
    ],
}


def _find_best_category(description: str) -> tuple[str, bool]:
    """
    Match description against keyword groups. Returns (category, is_ambiguous).
    """
    desc_lower = description.lower()
    scores: dict[str, int] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in desc_lower:
                score += 1
        if score > 0:
            scores[category] = score

    if not scores:
        return "Other", True

    max_score = max(scores.values())
    top_categories = [cat for cat, s in scores.items() if s == max_score]

    if len(top_categories) > 1:
        return top_categories[0], True

    return top_categories[0], False


def _determine_priority(description: str) -> str:
    """
    Return Urgent if any severity keyword is found, else Standard.
    """
    desc_lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", desc_lower):
            return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Build a one-sentence reason citing specific words from the description.
    """
    desc_lower = description.lower()
    cited_words = []

    if category != "Other":
        keywords = CATEGORY_KEYWORDS.get(category, [])
        for kw in keywords:
            if kw in desc_lower:
                cited_words.append(kw)
                break

    if priority == "Urgent":
        for kw in SEVERITY_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", desc_lower):
                cited_words.append(kw)
                break

    if not cited_words:
        return f"Classified as '{category}' based on overall description content."

    quoted = ", ".join(f'"{w}"' for w in cited_words)
    return f"Classified as {category} because the description mentions {quoted}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules (from agents.md):
    - Category must be exactly one of the 10 allowed values.
    - Priority must be Urgent if severity keywords are present.
    - Reason must cite specific words from the description.
    - Flag NEEDS_REVIEW if category is ambiguous or description is empty.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("complaint_description", "")

    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _find_best_category(description)
    priority = _determine_priority(description)
    reason = _build_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

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

    Handles errors gracefully:
    - Flags null / malformed rows instead of crashing.
    - Produces output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", f"row_{i}"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row could not be processed.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
