"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re

VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]
VALID_PRIORITIES = ["Urgent", "Standard", "Low"]
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = [
    (r"\bheritage\b", "Heritage Damage"),
    (r"\bdrain\b.*\b(block|clog|chok)", "Drain Blockage"),
    (r"\b(block|clog|chok).*\bdrain\b", "Drain Blockage"),
    (r"\bdrain(?:ing|ed)?\b.*\b(road|public)\b", "Drain Blockage"),
    (r"\bpothole", "Pothole"),
    (r"\bflood(?:ed|ing|s)\b", "Flooding"),
    (r"\brainwater\b", "Flooding"),
    (r"\bstreet\s*light", "Streetlight"),
    (r"\blights?\s*out\b", "Streetlight"),
    (r"\bunlit\b", "Streetlight"),
    (r"\bdarkness\b", "Streetlight"),
    (r"\bgarbage\b|\bwaste\b|\btrash\b|\brubbish\b|\bdead animal\b", "Waste"),
    (r"\bnoise\b|\bloud\b|\bmusic\b|\bdrilling\b|\bidling\b|\bamplifier", "Noise"),
    (r"\bconstruction\b.*\b(drill|noise|work)\b", "Noise"),
    (r"\bband\b.*\bplaying\b", "Noise"),
    (r"\broad\b.*\bcrack(?:ed|ing)?\b", "Road Damage"),
    (r"\broad\b.*\bsink(?:ing)?\b", "Road Damage"),
    (r"\broad\b.*\bsubsid(?:ed|ence)\b", "Road Damage"),
    (r"\broad\b.*\bbuckl(?:ed|ing)\b", "Road Damage"),
    (r"\broad\b.*\bdamag(?:ed|e)?\b", "Road Damage"),
    (r"\broad\b.*\bbroken\b", "Road Damage"),
    (r"\broad\b.*\bbreak(?:ing)?\b", "Road Damage"),
    (r"\broad\b.*\bcollaps(?:ed|e|ing)\b", "Road Damage"),
    (r"\broad\b.*\bcrater\b", "Road Damage"),
    (r"\bcrack(?:ed|ing)?\b.*\broad\b", "Road Damage"),
    (r"\bpaving\b|\bfootpath\b|\bmanhole\b", "Road Damage"),
    (r"\bbench\b.*\b(upturn|broken)\b", "Road Damage"),
    (r"\bheat\b|\btemperature\w*\b|\bscorching\b|\bheatwave\b|\°C\b|\bcelsius\b|\bmelting\b|\bbubbling\b", "Heat Hazard"),
    (r"\b(dangerous|unbearable|extreme)\b.*\b(temperature\w*|heat)\b", "Heat Hazard"),
    (r"\b(temperature\w*)\b.*\b(dangerous|unbearable|extreme)\b", "Heat Hazard"),
]


def _has_severity_keyword(description: str) -> bool:
    lower = description.lower()
    return any(kw in lower for kw in SEVERITY_KEYWORDS)


def _detect_category(description: str) -> str:
    lower = description.lower()
    for pattern, category in CATEGORY_RULES:
        if re.search(pattern, lower):
            return category
    return "Other"


def _build_reason(description: str, category: str) -> str:
    lower = description.lower()
    if category == "Pothole":
        match = re.search(r"(.{0,40}pothole.{0,40})", lower)
    elif category == "Flooding":
        match = re.search(r"(.{0,40}(?:flood|rainwater).{0,40})", lower)
    elif category == "Streetlight":
        match = re.search(r"(.{0,40}(?:street\s*light|lights?\s*out|unlit|darkness).{0,40})", lower)
    elif category == "Waste":
        match = re.search(r"(.{0,40}(?:garbage|waste|trash|dead animal).{0,40})", lower)
    elif category == "Noise":
        match = re.search(r"(.{0,40}(?:noise|music|drill|idling|amplifier|band.*playing).{0,40})", lower)
    elif category == "Road Damage":
        match = re.search(r"(.{0,40}(?:road|footpath|manhole|paving|crack|broken|tiles|collapsed|crater|buckl|subsiden).{0,40})", lower)
    elif category == "Heritage Damage":
        match = re.search(r"(.{0,40}heritage.{0,40})", lower)
    elif category == "Heat Hazard":
        match = re.search(r"(.{0,40}(?:heat|temperature\w*|°C|melting|bubbling|scorching).{0,40})", lower)
    elif category == "Drain Blockage":
        match = re.search(r"(.{0,40}(?:drain|blocked|clog).{0,40})", lower)
    else:
        match = None

    if match:
        snippet = match.group(0).strip().strip(".,")
        return f"Description states \"{snippet}\"."
    return f"Description indicates a {category.lower()} issue."


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    if not complaint_id:
        raise ValueError("Missing complaint_id in input row")

    description = row.get("description", "").strip()
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    category = _detect_category(description)
    priority = "Urgent" if _has_severity_keyword(description) else "Standard"
    reason = _build_reason(description, category)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.isdir(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    results = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Row processing error.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
