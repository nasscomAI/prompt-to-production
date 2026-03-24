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

CATEGORY_RULES: List[Tuple[str, List[str]]] = [
    ("Drain Blockage", ["drain block", "blocked drain", "sewer block", "choked drain", "manhole"]),
    ("Flooding", ["flood", "waterlogging", "water logged", "water logging"]),
    ("Heritage Damage", ["heritage", "monument", "historic wall", "old structure", "step well", "old city"]),
    ("Streetlight", ["streetlight", "street light", "dark road", "unlit", "no lights", "lights out", "light not working", "wiring theft"]),
    ("Pothole", ["pothole", "crater", "big hole"]),
    ("Road Damage", ["road damaged", "road damage", "broken road", "cracked road", "road surface cracked", "uneven road", "sinking", "footpath", "tiles broken"]),
    ("Waste", ["garbage", "trash", "waste", "dumping", "bin overflow", "bins overflowing", "not cleared", "stink", "dead animal", "not removed"]),
    ("Noise", ["noise", "loudspeaker", "construction sound", "horn", "dj", "music audible", "music past midnight", "past midnight", "2am", "loud music"]),
    ("Heat Hazard", ["heat", "heatwave", "44°c", "45°c", "52°c", "full sun", "dangerous temperatures", "surface melting", "unbearable", "burns on contact", "temperature"]),
]


def _combined_text(row: dict) -> str:
    parts = []
    for key, value in row.items():
        if value is None:
            continue
        text = str(value).strip()
        if text:
            parts.append(text)
    return " ".join(parts).lower()


def _pick_reason(text: str, matched_keyword: str = "") -> str:
    if matched_keyword:
        return f"Marked based on complaint text containing '{matched_keyword}'."
    snippet = text[:80].strip() if text else "no usable complaint text"
    return f"Marked from complaint text: '{snippet}'."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = str(row.get("complaint_id", "")).strip() or "UNKNOWN"
    text = _combined_text(row)

    category = "Other"
    flag = "NEEDS_REVIEW"
    matched_keyword = ""

    match = None
    for candidate, keywords in CATEGORY_RULES:
        for keyword in keywords:
            if keyword in text:
                match = (candidate, keyword)
                break
        if match:
            break

    if match:
        category, matched_keyword = match
        flag = ""

    priority = "Standard"
    severity_hit = ""
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            priority = "Urgent"
            severity_hit = keyword
            break

    reason_keyword = severity_hit or matched_keyword
    reason = _pick_reason(text, reason_keyword)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
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
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", newline="", encoding="utf-8") as in_file, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as out_file:
        reader = csv.DictReader(in_file)
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                fallback_id = str(row.get("complaint_id", "")).strip() or "UNKNOWN"
                text = _combined_text(row)
                priority = "Urgent" if any(k in text for k in SEVERITY_KEYWORDS) else "Standard"
                result = {
                    "complaint_id": fallback_id,
                    "category": "Other",
                    "priority": priority,
                    "reason": "Marked NEEDS_REVIEW because row could not be classified safely.",
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
