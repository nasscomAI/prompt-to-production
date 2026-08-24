"""
UC-0A — Complaint Classifier
Implementation adhering to RICE framework (agents.md) and skills specification (skills.md).
"""
import argparse
import csv
import os
import re
from typing import Dict, Any

# Exact taxonomy defined in schema
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

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury",
    "injur",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "fall",
    "collapse",
]

# Category pattern heuristics
CATEGORY_RULES = {
    "Pothole": [
        r"\bpothole[s]?\b",
        r"\bcrater\b",
    ],
    "Drain Blockage": [
        r"\bdrain\b.*?\bblock",
        r"\bblocked drain\b",
        r"\bstormwater drain\b",
        r"\bclogged drain\b",
        r"\bchannel rainwater\b",
        r"\bdraining directly\b",
    ],
    "Flooding": [
        r"\bflood(ed|ing|s)?\b",
        r"\bwaterlogging\b",
        r"\bstanding in water\b",
        r"\bknee-deep\b",
    ],
    "Streetlight": [
        r"\bstreetlight[s]?\b",
        r"\blamp post\b",
        r"\bunlit\b",
        r"\bdarkness\b",
        r"\blights out\b",
        r"\belectrical hazard\b",
        r"\bsubstation tripped\b",
    ],
    "Waste": [
        r"\bgarbage\b",
        r"\bwaste\b",
        r"\bdead animal\b",
        r"\boverflowing bins?\b",
        r"\bdumped\b",
        r"\brubbish\b",
        r"\bdebris\b",
    ],
    "Noise": [
        r"\bmusic\b",
        r"\bdrilling\b",
        r"\bamplifier[s]?\b",
        r"\bwedding band\b",
        r"\bloud\b",
        r"\bidling with engines\b",
    ],
    "Heritage Damage": [
        r"\bheritage\b",
        r"\bhistoric\b",
        r"\bcobblestone[s]?\b",
        r"\btram road\b",
        r"\bmonument\b",
        r"\bstep well\b",
        r"\bancient\b",
    ],
    "Heat Hazard": [
        r"\b\d+°C\b",
        r"\bmelting\b",
        r"\bheatwave\b",
        r"\bheating\b",
        r"\btemperature[s]?\b",
        r"\bburns on contact\b",
        r"\bdead trees\b",
        r"\bgrass dying\b",
        r"\bfull sun\b",
    ],
    "Road Damage": [
        r"\bfootpath\b",
        r"\btiles broken\b",
        r"\bcracked and sinking\b",
        r"\bmanhole\b",
        r"\bbuckled\b",
        r"\bsubsidence\b",
        r"\bbroken bench\b",
        r"\broad surface\b",
        r"\bcollapsed\b",
    ],
}


def _extract_citation(text: str, trigger_word: str = None) -> str:
    """Extract a representative quoted snippet or the specific trigger sentence from description."""
    if not text:
        return "no description provided"
    # Split text into distinct sentences / clauses
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    if trigger_word:
        for s in sentences:
            if re.search(r"\b" + re.escape(trigger_word), s, re.IGNORECASE):
                # Clean trailing period for neat formatting in quotation
                return s.rstrip(".")
    if sentences:
        return sentences[0].rstrip(".")
    return text.strip().rstrip(".")


def classify_complaint(row: Dict[str, Any]) -> Dict[str, str]:
    """
    Classify a single complaint row into category, priority, reason, and flag.
    Adheres strictly to RICE enforcement rules in agents.md.
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": 'Description is missing or empty, unable to determine grievance category.',
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # 1. Determine Priority via severity triggers
    is_urgent = False
    urgent_word = None
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw), desc_lower):
            is_urgent = True
            urgent_word = kw
            break

    priority = "Urgent" if is_urgent else "Standard"

    # 2. Determine Category matching scores
    category_scores = {}
    for cat, patterns in CATEGORY_RULES.items():
        score = 0
        for pat in patterns:
            if re.search(pat, desc_lower):
                score += 1
        if score > 0:
            category_scores[cat] = score

    # Disambiguation heuristics
    assigned_category = "Other"
    flag = ""

    if not category_scores:
        assigned_category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(category_scores) == 1:
        assigned_category = list(category_scores.keys())[0]
    else:
        # Precedence & contextual rules
        if "Heritage Damage" in category_scores and any(w in desc_lower for w in ["heritage", "historic", "ancient", "cobblestone"]):
            # If heritage context is prominent, classify as Heritage Damage unless pure waste/noise
            if "Waste" in category_scores and "waste" in desc_lower and "overflow" in desc_lower:
                assigned_category = "Waste"
            elif "Noise" in category_scores and ("music" in desc_lower or "amplifier" in desc_lower or "band" in desc_lower):
                assigned_category = "Noise"
            else:
                assigned_category = "Heritage Damage"
        elif "Pothole" in category_scores and "pothole" in desc_lower:
            assigned_category = "Pothole"
        elif "Drain Blockage" in category_scores and ("drain" in desc_lower or "stormwater" in desc_lower):
            assigned_category = "Drain Blockage"
        elif "Flooding" in category_scores and "flood" in desc_lower:
            assigned_category = "Flooding"
        elif "Heat Hazard" in category_scores and ("°c" in desc_lower or "melting" in desc_lower or "heat" in desc_lower or "temperature" in desc_lower):
            assigned_category = "Heat Hazard"
        elif "Streetlight" in category_scores and ("streetlight" in desc_lower or "lamp post" in desc_lower or "unlit" in desc_lower):
            assigned_category = "Streetlight"
        elif "Waste" in category_scores:
            assigned_category = "Waste"
        elif "Road Damage" in category_scores:
            assigned_category = "Road Damage"
        else:
            assigned_category = list(category_scores.keys())[0]
            flag = "NEEDS_REVIEW"

    # Verify category is in allowed set
    if assigned_category not in ALLOWED_CATEGORIES:
        assigned_category = "Other"
        flag = "NEEDS_REVIEW"

    # 3. Generate Citation and Single Sentence Reason
    citation = _extract_citation(description, urgent_word if is_urgent else None)
    if priority == "Urgent":
        reason = f'Classified as {assigned_category} with Urgent priority because the complaint description explicitly reports "{citation}".'
    else:
        reason = f'Classified as {assigned_category} with {priority} priority based on citizen report citing "{citation}".'

    return {
        "complaint_id": complaint_id,
        "category": assigned_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must handle missing/bad rows without crashing.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        for idx, row in enumerate(reader, start=1):
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as exc:
                # Gracefully recover on bad rows
                complaint_id = row.get("complaint_id", f"ROW-{idx}") if isinstance(row, dict) else f"ROW-{idx}"
                results.append({
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f'Row processing encountered an error: {str(exc)}.',
                    "flag": "NEEDS_REVIEW",
                })

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
