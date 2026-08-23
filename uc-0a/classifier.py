"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md workflow. Imthiaz Ahmed
"""
import argparse
import csv
import re
from typing import Dict

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


def classify_complaint(row: Dict) -> Dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
    description = row.get("description", "") if isinstance(row, dict) else ""

    # Error handling for missing or null description
    if not description or not isinstance(description, str) or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing or invalid.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # 1. Priority Determination (Check severity keywords)
    found_severity_words = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw), desc_lower):
            found_severity_words.append(kw)

    if found_severity_words:
        priority = "Urgent"
    elif any(term in desc_lower for term in ["music", "idling", "delivery trucks"]):
        priority = "Low"
    else:
        priority = "Standard"

    # 2. Category Determination & Ambiguity Identification
    matched_categories = set()
    cite_phrases = []

    if re.search(r'\bpotholes?\b|\bcrater\b|\bpit in road\b', desc_lower):
        matched_categories.add("Pothole")
        match = re.search(r'(potholes?|crater|pit in road)', desc_lower)
        if match:
            cite_phrases.append(match.group(0))

    if re.search(r'\bflood|\bflooded\b|\bflooding\b|\bfloods\b|\bwaterlogging\b|\bknee-deep\b|\bstanding in water\b|\bdraining\b', desc_lower):
        matched_categories.add("Flooding")
        match = re.search(r'(flooded|flooding|floods|waterlogging|knee-deep|standing in water|draining)', desc_lower)
        if match:
            cite_phrases.append(match.group(0))

    if re.search(r'\bdrain\b|\bgutter\b|\bsewer\b|\bstormwater\b', desc_lower):
        if re.search(r'\bblocked\b|\bchoked\b|\bdebris\b|\bmosquito\b|\bbreeding\b', desc_lower):
            matched_categories.add("Drain Blockage")
            cite_phrases.append("drain blocked")

    if re.search(r'\bstreetlights?\b|\blamp post\b|\bdarkness\b|\bunlit\b|\blights? out\b|\blight out\b', desc_lower):
        matched_categories.add("Streetlight")
        match = re.search(r'(streetlights?|lamp post|darkness|unlit|lights? out)', desc_lower)
        if match:
            cite_phrases.append(match.group(0))

    if re.search(r'\bgarbage\b|\bwaste\b|\btrash\b|\bdead animal\b|\blitter\b|\brefuse\b|\bdumped\b', desc_lower):
        matched_categories.add("Waste")
        match = re.search(r'(garbage|waste|trash|dead animal|litter|dumped)', desc_lower)
        if match:
            cite_phrases.append(match.group(0))

    if re.search(r'\bmusic\b|\bnoise\b|\bamplifiers\b|\bdrilling\b|\bloudspeakers\b|\bidling\b|\baudible\b|\bband\b|\bplaying\b|\bloud\b', desc_lower):
        matched_categories.add("Noise")
        match = re.search(r'(music|noise|amplifiers|drilling|loudspeakers|idling|band|playing|loud)', desc_lower)
        if match:
            cite_phrases.append(match.group(0))

    if re.search(r'\bheat\b|\bheatwave\b|\bmelting\b|\btemperatures?\b|\b44°c\b|\b45°c\b|\b52°c\b|\bfull sun\b|\bburns\b', desc_lower):
        matched_categories.add("Heat Hazard")
        match = re.search(r'(heat|heatwave|melting|temperatures?|full sun|burns)', desc_lower)
        if match:
            cite_phrases.append(match.group(0))

    if re.search(r'\bheritage\b|\bhistoric\b|\btram road\b|\bancient\b|\bmonument\b', desc_lower):
        matched_categories.add("Heritage Damage")
        match = re.search(r'(heritage|historic|ancient)', desc_lower)
        if match:
            cite_phrases.append(match.group(0))

    if re.search(r'\broad surface\b|\bfootpath\b|\bpavement\b|\bpaving\b|\bsubsided\b|\bsubsidence\b|\bcracked\b|\bsinking\b|\bmanhole\b|\bbuckled\b|\bcobblestones\b|\bcollapse\b|\bcollapsed\b|\broad dividers?\b', desc_lower):
        if "Pothole" not in matched_categories:
            matched_categories.add("Road Damage")
            match = re.search(r'(road surface|footpath|pavement|paving|subsidence|cracked|sinking|manhole|buckled|collapsed)', desc_lower)
            if match:
                cite_phrases.append(match.group(0))

    # Resolve Primary Category and Flag
    flag = ""
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = list(matched_categories)[0]
    else:
        # Multi-category ambiguity handling
        if "Heritage Damage" in matched_categories and "Streetlight" in matched_categories:
            category = "Streetlight"
            flag = "NEEDS_REVIEW"
        elif "Heritage Damage" in matched_categories and "Waste" in matched_categories:
            category = "Waste"
            flag = "NEEDS_REVIEW"
        elif "Heritage Damage" in matched_categories and "Noise" in matched_categories:
            category = "Noise"
            flag = "NEEDS_REVIEW"
        elif "Heritage Damage" in matched_categories and "Road Damage" in matched_categories:
            category = "Heritage Damage"
            flag = "NEEDS_REVIEW"
        elif "Flooding" in matched_categories and "Drain Blockage" in matched_categories:
            category = "Drain Blockage"
            flag = "NEEDS_REVIEW"
        else:
            category = list(matched_categories)[0]
            flag = "NEEDS_REVIEW"

    # Construct Reason (Single sentence citing specific words from description)
    citation = cite_phrases[0] if cite_phrases else description[:30]
    if found_severity_words:
        reason = f"Classified as {category} with {priority} priority because description cites '{citation}' and severity keyword '{found_severity_words[0]}'."
    else:
        reason = f"Classified as {category} with {priority} priority because description cites '{citation}'."

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
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig", errors="replace") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as e:
                complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
                classified = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing error encountered: {str(e)}.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(classified)

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

