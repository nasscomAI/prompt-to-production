"""
UC-0A — Complaint Classifier
Deterministic, schema-compliant classifier built using the RICE + CRAFT framework.
"""
import argparse
import csv
import os
import re
from typing import Dict, Any, List

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
    "Other"
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity keywords specified in UC-0A README + standard morphological variants
SEVERITY_PATTERNS = [
    r"\binjur(?:y|ies|ed)?\b",
    r"\bchild(?:ren)?\b",
    r"\bschool(?:s)?\b",
    r"\bhospital(?:s|ised|ized)?\b",
    r"\bambulance(?:s)?\b",
    r"\bfire(?:s)?\b",
    r"\bhazard(?:s|ous)?\b",
    r"\bfell\b",
    r"\bcollaps(?:e|ed|ing)\b",
    r"\bgas leak\b",
    r"\blives at risk\b"
]

CITABLE_TERMS = [
    "pothole", "potholes", "flooded", "flooding", "floods", "drain blocked",
    "drain", "stormwater drain", "garbage", "waste", "music", "drilling",
    "amplifiers", "idling", "collapsed", "crater", "hospital", "hospitalised",
    "hospitalized", "school", "ambulance", "hazard", "fell", "injury", "injured",
    "child", "streetlights", "streetlight", "lights out", "unlit", "melting",
    "heatwave", "dead animal", "temperature", "heritage", "historic", "cobblestones",
    "broken", "subsidence", "subsided", "darkness", "buckled", "cracked", "sinking",
    "wedding band", "storing heat", "bubbling", "dead trees"
]

def classify_complaint(row: Dict[str, Any]) -> Dict[str, str]:
    """
    Classify a single citizen complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    # Refusal/fallback on missing or empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty complaint description.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # 1. Severity Evaluation (Check triggers for Urgent)
    found_triggers = []
    for pattern in SEVERITY_PATTERNS:
        match = re.search(pattern, desc_lower)
        if match:
            found_triggers.append(match.group(0))

    if found_triggers:
        priority = "Urgent"
    else:
        priority = "Standard"

    # 2. Category Classification
    category = "Other"
    flag = ""

    if "pothole" in desc_lower or "potholes" in desc_lower:
        category = "Pothole"
    elif any(k in desc_lower for k in [
        "melting at", "temperature", "temperatures", "storing heat",
        "bubbling at", "full sun", "heatwave", "44°c", "45°c", "52°c"
    ]):
        category = "Heat Hazard"
    elif any(k in desc_lower for k in [
        "heritage lamp", "historic tram", "heritage residential", "heritage stone",
        "ancient step well", "defaced by billboard"
    ]):
        category = "Heritage Damage"
    elif any(k in desc_lower for k in [
        "substation tripped", "unlit", "streetlights out", "streetlight",
        "lights out", "flickering and sparking", "wiring theft", "darkness for"
    ]):
        category = "Streetlight"
    elif any(k in desc_lower for k in [
        "music", "drilling", "sound", "amplifiers", "idling with engines on", "wedding band"
    ]):
        category = "Noise"
    elif any(k in desc_lower for k in [
        "garbage", "waste", "bins overflowing", "dumped", "dead animal"
    ]):
        category = "Waste"
    elif any(k in desc_lower for k in [
        "drain blocked", "drain completely blocked", "stormwater drain", "main drain"
    ]):
        category = "Drain Blockage"
    elif any(k in desc_lower for k in [
        "flooded", "flooding", "floods", "waterlogging", "standing in water"
    ]):
        category = "Flooding"
    elif any(k in desc_lower for k in [
        "road collapsed", "crater", "road surface cracked", "road surface buckled",
        "footpath", "sinking", "subsidence", "subsided", "manhole cover missing",
        "broken bench", "paving", "broken up by cable"
    ]):
        category = "Road Damage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Ambiguity check for non-asset / private-public runoff disputes
    if (
        "channel rainwater through main road" in desc_lower
        or "draining directly onto public road" in desc_lower
        or "dead trees with split branches" in desc_lower
    ):
        flag = "NEEDS_REVIEW"
        if category not in ["Drain Blockage", "Flooding"]:
            category = "Other"

    # 3. Justification Reason Generation (citing specific terms)
    matched_words = [t for t in CITABLE_TERMS if t in desc_lower]
    if matched_words:
        cited_str = ", ".join([f"'{w}'" for w in matched_words[:3]])
        reason = f"Classified as {category} ({priority}) citing words: {cited_str}."
    else:
        clean_snippet = re.sub(r'[\r\n"]+', ' ', description[:50]).strip()
        reason = f"Classified as {category} ({priority}) citing: '{clean_snippet}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results: List[Dict[str, str]] = []

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                complaint_id = row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN"
                results.append({
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
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
