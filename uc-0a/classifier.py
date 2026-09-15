"""
UC-0A — Complaint Classifier
Implementation guided by RICE agents.md and skills.md.
"""
import argparse
import csv
import os
import re
from typing import Dict, Any, Tuple

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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity triggers that must escalate priority to Urgent
SEVERITY_REGEX = re.compile(
    r"\b(injury|injuries|injured|child|children|school|hospital|hospitalised|hospitalized|ambulance|fire|hazard|hazardous|fell|collapse|collapsed|collapsing)\b",
    re.IGNORECASE,
)

# Pattern definitions for municipal categories
POTHOLE_PATTERN = re.compile(r"\b(pothole|potholes)\b", re.IGNORECASE)

HEAT_HAZARD_PATTERN = re.compile(
    r"\b(heat|temperatures?|44°c|45°c|52°c|melting at|heatwave|storing heat|burns on contact|full sun)\b",
    re.IGNORECASE,
)

HERITAGE_DAMAGE_PATTERN = re.compile(
    r"(\bheritage\b.*\b(knocked over|defaced|damaged|not replaced|restored)\b|"
    r"\bhistoric tram\b.*\b(broken|cobblestone)\b|"
    r"\bancient step well\b|"
    r"\bheritage stone not replaced\b|"
    r"\bheritage.*defaced\b)",
    re.IGNORECASE,
)

DRAIN_BLOCKAGE_PATTERN = re.compile(
    r"\b(drain blocked|drain completely blocked|drain blockage|stormwater drain|main drain blocked|draining directly|drainage|sewer blocked)\b",
    re.IGNORECASE,
)

FLOODING_PATTERN = re.compile(
    r"\b(flood|floods|flooded|flooding|waterlogging|knee-deep|standing in water|rainwater through main road)\b",
    re.IGNORECASE,
)

STREETLIGHT_PATTERN = re.compile(
    r"\b(streetlight|streetlights|lights out|unlit|dark at night|lamp post|sparking)\b",
    re.IGNORECASE,
)

NOISE_PATTERN = re.compile(
    r"\b(music|wedding band|wedding venue|drilling|trucks idling|engines on|amplifiers|noise)\b",
    re.IGNORECASE,
)

WASTE_PATTERN = re.compile(
    r"\b(garbage|waste|bins overflowing|overflowing garbage|dumped|dead animal|trash|litter)\b",
    re.IGNORECASE,
)

ROAD_DAMAGE_PATTERN = re.compile(
    r"\b(road surface cracked|road surface buckled|cracked and sinking|manhole cover missing|"
    r"road collapsed|footpath tiles broken|footpath broken|road subsided|upturned paving|crater)\b",
    re.IGNORECASE,
)


def _extract_citation(text: str, match_obj) -> str:
    """Extract a complete sentence or clause around a match from description without truncating words."""
    if not match_obj:
        return text.split(".")[0].strip()
    
    # Split text into clean sentences or clauses
    clauses = [c.strip() for c in re.split(r"[.;\n]", text) if c.strip()]
    matched_text = match_obj.group(0).lower()
    for clause in clauses:
        if matched_text in clause.lower():
            return clause
            
    return match_obj.group(0)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Adheres strictly to R.I.C.E rules:
    - category must be one of the 10 allowed categories.
    - priority must be Urgent if severity keywords are present.
    - reason must be exactly one sentence citing specific words from description.
    - flag is set to NEEDS_REVIEW when genuinely ambiguous or category is Other.
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    raw_desc = row.get("description")

    # Handle missing or empty description
    if raw_desc is None or not str(raw_desc).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": 'Classified as Other with NEEDS_REVIEW because the complaint description is missing or empty.',
            "flag": "NEEDS_REVIEW",
        }

    description = str(raw_desc).strip()

    # 1. Severity check (prevents severity blindness)
    sev_match = SEVERITY_REGEX.search(description)
    if sev_match:
        priority = "Urgent"
        trigger_word = sev_match.group(0)
    else:
        priority = "Standard"
        trigger_word = None

    # 2. Category matching
    category = None
    matched_quote = ""

    # Check Pothole first (specific road hazard)
    pothole_m = POTHOLE_PATTERN.search(description)
    if pothole_m:
        category = "Pothole"
        matched_quote = _extract_citation(description, pothole_m)

    # Check Heritage Damage (specific historic asset damage)
    if not category:
        heritage_m = HERITAGE_DAMAGE_PATTERN.search(description)
        if heritage_m:
            category = "Heritage Damage"
            matched_quote = _extract_citation(description, heritage_m)

    # Check Heat Hazard
    if not category:
        heat_m = HEAT_HAZARD_PATTERN.search(description)
        if heat_m:
            category = "Heat Hazard"
            matched_quote = _extract_citation(description, heat_m)

    # Check Drain Blockage (direct structural blockage)
    if not category:
        drain_m = DRAIN_BLOCKAGE_PATTERN.search(description)
        if drain_m:
            category = "Drain Blockage"
            matched_quote = _extract_citation(description, drain_m)

    # Check Flooding
    if not category:
        flood_m = FLOODING_PATTERN.search(description)
        if flood_m:
            category = "Flooding"
            matched_quote = _extract_citation(description, flood_m)

    # Check Noise
    if not category:
        noise_m = NOISE_PATTERN.search(description)
        if noise_m:
            category = "Noise"
            matched_quote = _extract_citation(description, noise_m)

    # Check Waste
    if not category:
        waste_m = WASTE_PATTERN.search(description)
        if waste_m:
            category = "Waste"
            matched_quote = _extract_citation(description, waste_m)

    # Check Streetlight (excluding power grid substation failure)
    if not category:
        if "substation" not in description.lower():
            light_m = STREETLIGHT_PATTERN.search(description)
            if light_m:
                category = "Streetlight"
                matched_quote = _extract_citation(description, light_m)

    # Check Road Damage
    if not category:
        road_m = ROAD_DAMAGE_PATTERN.search(description)
        if road_m:
            category = "Road Damage"
            matched_quote = _extract_citation(description, road_m)

    # 3. Fallback / Refusal condition for ambiguous or unmapped complaints
    if category is None or category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        matched_quote = _extract_citation(description, None)
        if trigger_word:
            reason = (
                f'Classified as Other with NEEDS_REVIEW because the description citing "{matched_quote}" '
                f'does not fit standard categories despite urgent trigger "{trigger_word}".'
            )
        else:
            reason = (
                f'Classified as Other with NEEDS_REVIEW because the description citing "{matched_quote}" '
                f'does not clearly match standard municipal categories.'
            )
    else:
        flag = ""
        if priority == "Urgent" and trigger_word:
            reason = (
                f'Classified as {category} with Urgent priority due to safety trigger "{trigger_word}", '
                f'evidenced by "{matched_quote}".'
            )
        else:
            reason = (
                f'Classified as {category} with Standard priority based on description citing "{matched_quote}".'
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
    Guarantees robust error handling: does not crash on malformed rows,
    flags nulls/anomalies, and produces valid output for every record.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as exc:
                cid = row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN"
                classified = {
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f'Classified as Other with NEEDS_REVIEW due to processing exception: "{exc}".',
                    "flag": "NEEDS_REVIEW",
                }
            results.append(classified)

    # Ensure output directory exists if provided
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
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
