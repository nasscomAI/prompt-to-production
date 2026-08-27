"""
UC-0A — Complaint Classifier
Build guided by agents.md (RICE framework) and skills.md.
"""
import argparse
import csv
import os
import re
import sys
from typing import Dict, Any, List, Optional, Tuple

# Exact allowed categories from classification schema
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

# Severity keywords triggering 'Urgent' priority
SEVERITY_REGEX = re.compile(
    r"\b(injury|injured|injuries|child|children|school|hospital|hospitalised|hospitalized|ambulance|fire|hazard|hazardous|fell|fall|collapse|collapsed|collapsing|gas leak)\b",
    re.IGNORECASE,
)


def _extract_severity(text: str) -> Tuple[str, Optional[str]]:
    """
    Evaluates priority based on severity keywords.
    Returns: (priority: "Urgent" | "Standard" | "Low", matched_keyword: str | None)
    """
    if not text:
        return "Standard", None

    match = SEVERITY_REGEX.search(text)
    if match:
        return "Urgent", match.group(0)

    return "Standard", None


def _find_snippet(text: str, match_term: str) -> str:
    """Extracts a concise, readable snippet around a matched keyword for evidence citation."""
    if not text or not match_term:
        return ""
    pos = text.lower().find(match_term.lower())
    if pos == -1:
        return match_term
    start = max(0, pos - 12)
    end = min(len(text), pos + len(match_term) + 15)
    snippet = text[start:end].strip(" ,.;:-")
    return snippet


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()
    location = str(row.get("location", "")).strip()
    ward = str(row.get("ward", "")).strip()

    # Ambiguity / Empty Description Refusal Condition
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty complaint description; cannot determine category from text.",
            "flag": "NEEDS_REVIEW",
        }

    full_text = f"{description} {location}"
    desc_lower = description.lower()

    # 1. Determine Priority
    priority, severity_trigger = _extract_severity(full_text)

    # 2. Determine Category based on rules and keyword cues
    category = "Other"
    category_evidence = ""
    is_ambiguous = False

    scores = {}

    # Pothole
    if re.search(r"\bpotholes?\b", desc_lower):
        scores["Pothole"] = 12
        category_evidence = re.search(r"\bpotholes?\b", description, re.IGNORECASE).group(0)

    # Heat Hazard (High precedence for extreme heat/temperature hazards)
    heat_match = re.search(r"\b(heat|heatwave|temperature|temperatures|\d+°c|bubbling|melting|storing heat|burns on contact|full sun)\b", desc_lower)
    if heat_match:
        scores["Heat Hazard"] = 11
        if not category_evidence:
            category_evidence = heat_match.group(0)

    # Noise
    noise_match = re.search(r"\b(music|drilling|amplifiers?|loud|noise|band playing|idling with engines?|loudspeakers?)\b", desc_lower)
    if noise_match:
        scores["Noise"] = 10
        if not category_evidence:
            category_evidence = noise_match.group(0)

    # Heritage Damage (Structural / aesthetic damage to heritage assets)
    heritage_damage_match = re.search(r"\b(heritage|historic|ancient|cobblestones?|heritage stone|monument|museum|step well)\b", desc_lower)
    if heritage_damage_match:
        if re.search(r"\b(broken|subsidence|defaced|knocked over|not replaced|cable laying|damage)\b", desc_lower):
            scores["Heritage Damage"] = 10
            if not category_evidence:
                category_evidence = heritage_damage_match.group(0)
        else:
            # Context only (e.g. noise in heritage precinct, waste in heritage zone)
            scores["Heritage Damage"] = 3

    # Waste
    waste_match = re.search(r"\b(garbage|waste|dead animal|dumped|bins? overflowing|debris)\b", desc_lower)
    if waste_match:
        if "drain" in desc_lower and "blocked" in desc_lower:
            scores["Drain Blockage"] = 9
            scores["Waste"] = 5
        else:
            scores["Waste"] = 9
        if not category_evidence:
            category_evidence = waste_match.group(0)

    # Drain Blockage
    drain_match = re.search(r"\b(drain|drains|draining|stormwater drain|drainage|manhole)\b", desc_lower)
    if drain_match and re.search(r"\b(blocked|debris|breeding|missing|cover|directly onto public road)\b", desc_lower):
        scores["Drain Blockage"] = 9
        if not category_evidence:
            category_evidence = drain_match.group(0)

    # Streetlight (lighting outages, sparking fixtures, wiring theft)
    light_match = re.search(r"\b(streetlights?|lamp post|lights? out|unlit|wiring theft|substation tripped|darkness)\b", desc_lower)
    if light_match and scores.get("Heritage Damage", 0) < 10:
        scores["Streetlight"] = 9
        if not category_evidence:
            category_evidence = light_match.group(0)

    # Flooding
    flood_match = re.search(r"\b(flooded|flooding|floods|standing in water|channel rainwater|rainwater|knee-deep)\b", desc_lower)
    if flood_match:
        if scores.get("Drain Blockage", 0) >= 9:
            scores["Flooding"] = 8
        else:
            scores["Flooding"] = 9
        if not category_evidence:
            category_evidence = flood_match.group(0)

    # Road Damage
    road_match = re.search(r"\b(road surface|tarmac|cracked|sinking|subsided|subsidence|footpath|paving|buckled|crater|collapse|collapsed|tiles broken)\b", desc_lower)
    if road_match and "Pothole" not in scores and scores.get("Heritage Damage", 0) < 10 and scores.get("Heat Hazard", 0) < 10:
        scores["Road Damage"] = 9
        if not category_evidence:
            category_evidence = road_match.group(0)

    # Pick highest scoring category
    if scores:
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_score = sorted_cats[0]
        if len(sorted_cats) > 1 and sorted_cats[1][1] == top_score and sorted_cats[1][0] != top_cat:
            is_ambiguous = True
            category = top_cat
        else:
            category = top_cat
    else:
        category = "Other"
        is_ambiguous = True

    # Validate against allowed categories schema
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        is_ambiguous = True

    # 3. Construct Reason citing specific words from description
    evidence_snippet = _find_snippet(description, category_evidence if category_evidence else description.split()[0])
    
    if priority == "Urgent":
        severity_snippet = _find_snippet(description, severity_trigger if severity_trigger else "urgent")
        reason = f"Classified as '{category}' citing '{evidence_snippet}' and assigned 'Urgent' priority due to safety trigger '{severity_snippet}'."
    else:
        reason = f"Classified as '{category}' citing '{evidence_snippet}' with '{priority}' priority as no severe life-safety keywords were found."

    # Ensure reason is strictly a single sentence
    reason = reason.replace("\n", " ").strip()
    if not reason.endswith("."):
        reason += "."

    # 4. Set Flag
    flag = "NEEDS_REVIEW" if (is_ambiguous or category == "Other") else ""

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
    Resilient to missing files, corrupt rows, and nulls.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        for idx, row in enumerate(reader, start=1):
            try:
                classified = classify_complaint(row)
            except Exception as e:
                complaint_id = row.get("complaint_id", f"ROW-{idx}")
                classified = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error occurred: {str(e)}.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(classified)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Processed {len(results)} complaints from '{input_path}' -> '{output_path}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
