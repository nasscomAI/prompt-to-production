"""
UC-0A — Complaint Classifier
Implementation based on RICE framework, agents.md, and skills.md.
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


def _detect_severity(text: str) -> Tuple[str, List[str]]:
    """Detect if severity triggers are present in the text."""
    lower_text = text.lower()
    matched = []
    
    # Check severity keywords with word/stem boundary checks
    for kw in SEVERITY_KEYWORDS:
        if kw == "fell":
            if re.search(r"\bfell\b", lower_text):
                matched.append(kw)
        elif kw == "fire":
            if re.search(r"\bfire\b", lower_text):
                matched.append(kw)
        elif kw == "child":
            if re.search(r"\bchild(ren)?\b", lower_text):
                matched.append(kw)
        elif kw == "collapse":
            if re.search(r"\bcollaps(e|ed|ing)?\b", lower_text):
                matched.append(kw)
        elif kw == "injury":
            if re.search(r"\binjur(y|ies|ed)?\b", lower_text):
                matched.append(kw)
        elif kw == "hospital":
            if re.search(r"\bhospital(ised|ized)?\b", lower_text):
                matched.append(kw)
        else:
            if kw in lower_text:
                matched.append(kw)

    if matched:
        return "Urgent", matched
    return "Standard", []


def _categorize(description: str, location: str) -> Tuple[str, str, str, str]:
    """
    Determine category, priority, reason, and flag.
    Returns: (category, priority, reason, flag)
    """
    text = f"{location} {description}".strip()
    if not description or not description.strip():
        return "Other", "Standard", "Missing or empty complaint description.", "NEEDS_REVIEW"

    desc_lower = description.lower()
    combined_lower = text.lower()

    priority, severity_matches = _detect_severity(combined_lower)

    # Category matching signals
    scores: Dict[str, List[str]] = {cat: [] for cat in ALLOWED_CATEGORIES if cat != "Other"}

    # 1. Pothole
    if re.search(r"\bpotholes?\b", desc_lower):
        scores["Pothole"].append("pothole")

    # 2. Heat Hazard
    if re.search(r"(\b\d{2}°c\b|\bheatwave\b|\bheat\b|\bmelting\b|\bbubbling\b|\bburns\b|\btemperatures?\b|\bfull sun\b)", desc_lower):
        scores["Heat Hazard"].append("heat hazard condition")

    # 3. Noise
    if re.search(r"(\bmusic\b|\bdrilling\b|\bnoise\b|\bamplifiers?\b|\bloud\b|\bsound\b|\bband\b|\bidling\b|\bengines on\b)", desc_lower):
        scores["Noise"].append("noise disturbance")

    # 4. Drain Blockage
    if re.search(r"(\bdrain(s|age)?\b|\bstormwater drain\b|\bmanhole\b|\bdraining directly\b)", desc_lower):
        scores["Drain Blockage"].append("drainage or drain blockage")

    # 5. Flooding
    if re.search(r"(\bflood(ed|ing|s)?\b|\bstanding in water\b|\bwaterlogging\b|\bknee-deep\b|\binundat(ed|ion)\b|\bchannel rainwater\b)", desc_lower):
        scores["Flooding"].append("flooding/waterlogging")

    # 6. Streetlight
    if re.search(r"(\bstreetlights?\b|\blamp post\b|\blights? out\b|\bunlit\b|\bflickering\b|\bsparking\b|\bdarkness\b|\belectrical\b|\bsubstation\b)", desc_lower):
        scores["Streetlight"].append("streetlight/electrical outage")

    # 7. Heritage Damage
    if re.search(r"(\bheritage\b|\bhistoric\b|\btram road\b|\bmuseum\b|\bancient\b|\bstatue\b|\bmonument\b)", combined_lower):
        if re.search(r"(\bdefaced\b|\bbroken up\b|\bknocked over\b|\bnot restored\b|\bsubsidence\b|\bheritage stone\b|\bheritage concern\b)", desc_lower):
            scores["Heritage Damage"].append("heritage damage")

    # 8. Waste
    if re.search(r"(\bgarbage\b|\bwaste\b|\bdead animal\b|\bbins?\b|\bdumped\b|\brubbish\b|\bdebris\b)", desc_lower):
        # If debris is specifically causing a drain blockage, prioritize drain blockage
        if not ("debris" in desc_lower and scores["Drain Blockage"]):
            scores["Waste"].append("waste/garbage")

    # 9. Road Damage
    if re.search(r"(\broad\b|\bfootpath\b|\bpaving\b|\btiles\b|\bbridge\b|\bcrater\b|\bsurface\b|\bsubsided\b|\bsinking\b|\bbuckled\b|\bcracked\b|\bcollapsed\b)", desc_lower):
        if not scores["Pothole"] and not scores["Heritage Damage"]:
            scores["Road Damage"].append("road infrastructure damage")

    # Match selection
    matched_categories = [cat for cat, sigs in scores.items() if sigs]

    category = "Other"
    flag = ""

    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        # Resolve hierarchical priorities based on specific root cause
        if "Heritage Damage" in matched_categories:
            category = "Heritage Damage"
        elif "Pothole" in matched_categories:
            category = "Pothole"
        elif "Drain Blockage" in matched_categories:
            category = "Drain Blockage"
        elif "Flooding" in matched_categories:
            category = "Flooding"
        elif "Heat Hazard" in matched_categories:
            category = "Heat Hazard"
        elif "Streetlight" in matched_categories:
            category = "Streetlight"
        elif "Waste" in matched_categories:
            category = "Waste"
        elif "Noise" in matched_categories:
            category = "Noise"
        elif "Road Damage" in matched_categories:
            category = "Road Damage"
        else:
            category = matched_categories[0]
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Construct quotation-backed one-sentence justification
    snippet = description.strip()
    if len(snippet) > 80:
        snippet = snippet[:77].rsplit(" ", 1)[0] + "..."

    if priority == "Urgent":
        sev_str = ", ".join(sorted(set(severity_matches)))
        reason = f"Classified as {category} (Urgent) citing severity trigger '{sev_str}' in '{snippet}'."
    else:
        reason = f"Classified as {category} ({priority}) based on citizen report stating '{snippet}'."

    return category, priority, reason, flag


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "")
    location = row.get("location", "")

    category, priority, reason, flag = _categorize(description, location)

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

    results = []
    with open(input_path, mode="r", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as e:
                classified = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during classification: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(classified)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    output_dir = os.path.dirname(output_path)
    if output_dir:
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
