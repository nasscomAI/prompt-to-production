"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from typing import Dict, List, Tuple


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
ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}
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

# Ordered from more specific to more general.
CATEGORY_RULES: List[Tuple[str, List[str]]] = [
    ("Drain Blockage", ["drain block", "blocked drain", "clogged drain", "sewer block"]),
    ("Flooding", ["flood", "waterlog", "water logging", "submerged", "overflowing water"]),
    ("Heat Hazard", ["heatstroke", "extreme heat", "heat wave", "no shade", "heat hazard"]),
    ("Heritage Damage", ["heritage", "monument", "historic", "temple wall", "protected site"]),
    ("Streetlight", ["streetlight", "street light", "lamp post", "dark street", "no light"]),
    ("Pothole", ["pothole", "crater on road", "road crater"]),
    ("Road Damage", ["road damage", "broken road", "cracked road", "damaged road", "road cave-in"]),
    ("Waste", ["garbage", "trash", "waste", "dumping", "litter", "bin overflow"]),
    ("Noise", ["noise", "loud music", "horn", "construction sound", "disturbance"]),
]


def _pick_description(row: Dict) -> str:
    """
    Choose the most likely text field for complaint details.
    """
    for key in ("description", "complaint", "complaint_text", "details", "text"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _contains_any(text: str, needles: List[str]) -> bool:
    return any(needle in text for needle in needles)


def _classify_category(description: str) -> Tuple[str, str]:
    """
    Return category and matched evidence phrase.
    """
    lowered = description.lower()
    matches: List[Tuple[str, str]] = []
    for category, keywords in CATEGORY_RULES:
        for keyword in keywords:
            if keyword in lowered:
                matches.append((category, keyword))
                break

    if not matches:
        return "Other", ""

    unique_categories = {category for category, _ in matches}
    if len(unique_categories) > 1:
        return "Other", ""

    return matches[0]


def _priority_from_description(description: str) -> Tuple[str, str]:
    lowered = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if keyword in lowered:
            return "Urgent", keyword
    return "Standard", ""


def _one_sentence(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return "Insufficient detail in complaint description."
    if cleaned.endswith("."):
        return cleaned
    return f"{cleaned}."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    description = _pick_description(row)

    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Insufficient detail in complaint description.",
            "flag": "NEEDS_REVIEW",
        }

    category, evidence = _classify_category(description)
    priority, urgency_keyword = _priority_from_description(description)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    if evidence:
        reason = f"Category set to {category} based on '{evidence}' in the complaint text"
    else:
        reason = "Description is ambiguous for category mapping from available keywords"

    if urgency_keyword:
        reason = f"{reason}; priority set to Urgent due to '{urgency_keyword}'"
    else:
        reason = f"{reason}; no urgency keyword found so priority is Standard"

    result = {
        "category": category if category in ALLOWED_CATEGORIES else "Other",
        "priority": priority if priority in ALLOWED_PRIORITIES else "Standard",
        "reason": _one_sentence(reason),
        "flag": flag if flag in {"NEEDS_REVIEW", ""} else "NEEDS_REVIEW",
    }
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")

        rows_out = []
        for row in reader:
            safe_row = dict(row or {})
            try:
                classification = classify_complaint(safe_row)
            except Exception as exc:  # Row-level fallback: continue batch.
                classification = {
                    "category": "Other",
                    "priority": "Standard",
                    "reason": _one_sentence(f"Row classification failed: {exc}"),
                    "flag": "NEEDS_REVIEW",
                }
            safe_row.update(classification)
            rows_out.append(safe_row)

    output_fields = list(reader.fieldnames)
    for required in ("category", "priority", "reason", "flag"):
        if required not in output_fields:
            output_fields.append(required)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
