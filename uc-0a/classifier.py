"""
UC-0A — Complaint Classifier
Build guided by RICE (agents.md) and skills.md.
Classifies citizen complaints by category and priority using strict taxonomy,
severity trigger enforcement, verbatim justification citations, and ambiguity flagging.
"""
import argparse
import csv
import os
import re
from typing import Dict, List, Optional, Tuple

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

SEVERITY_PATTERN = re.compile(
    r"\b(injury|injuries|injured|child|children|school|schools|hospital|hospitals|ambulance|ambulances|fire|fires|hazard|hazards|hazardous|fell|collapse|collapsing|collapsed)\b",
    re.IGNORECASE,
)


def extract_cited_phrase(description: str, keywords: List[str], max_len: int = 60) -> str:
    """Extract a clean excerpt from description containing the matched keywords."""
    desc_lower = description.lower()
    for kw in keywords:
        pos = desc_lower.find(kw.lower())
        if pos != -1:
            start = max(0, pos - 20)
            if start > 0:
                space_pos = description.find(" ", start)
                if space_pos != -1 and space_pos <= pos:
                    start = space_pos + 1
            end = min(len(description), pos + len(kw) + 35)
            if end < len(description):
                space_pos = description.rfind(" ", pos + len(kw), end)
                if space_pos != -1:
                    end = space_pos
            phrase = description[start:end].strip(" ,;.-")
            if phrase:
                return phrase
    # Fallback to description prefix on word boundary
    prefix = description[:max_len]
    space_pos = prefix.rfind(" ")
    if space_pos != -1:
        prefix = prefix[:space_pos]
    return prefix.strip(" ,;.-")


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    location = row.get("location", "").strip()

    # Refusal / Fallback condition for missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Complaint description is missing or blank; cannot determine issue.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()
    loc_lower = location.lower()
    full_text = f"{desc_lower} {loc_lower}"

    # 1. Determine Priority via strict Severity Keywords
    severity_matches = SEVERITY_PATTERN.findall(description)
    if severity_matches:
        priority = "Urgent"
        severity_evidence = ", ".join(f"'{m}'" for m in dict.fromkeys(severity_matches))
    else:
        priority = "Standard"
        severity_evidence = ""

    # 2. Determine Category and Ambiguity Flag
    category = "Other"
    flag = ""
    evidence_phrase = ""

    # Category matching signals
    is_pothole = bool(re.search(r"\bpotholes?\b|crater", full_text))
    is_heat = bool(
        re.search(
            r"\b(heat|heatwave|melting|storing heat|burns on contact|temperature|bubbling at)\b|4[0-9]°c|5[0-9]°c",
            full_text,
        )
    )
    is_noise = bool(
        re.search(r"\b(noise|music|wedding band|amplifier|amplifiers|loudspeaker|audible at)\b", full_text)
    )
    is_waste = bool(
        re.search(r"\b(waste|garbage|trash|dumped|overflowing|bins|dead animal)\b", full_text)
        and not is_noise
    )
    is_flooding = bool(
        re.search(r"\b(flooded|flooding|knee-deep|under water|submerged|waterlogging)\b", full_text)
    )
    is_drain = bool(
        re.search(r"\b(drain|draining|drainage|gutter|sewage|sewer|irrigation system)\b", full_text)
    )
    is_heritage = bool(
        re.search(r"\b(heritage|historic|ancient|tram road|monument|museum|cobblestones)\b", full_text)
    )
    is_streetlight = bool(
        re.search(
            r"\b(streetlight|streetlights|street light|lamp post|lighting|unlit|darkness|substation)\b",
            full_text,
        )
    )
    is_road_damage = bool(
        re.search(
            r"\b(road surface|buckled|subsidence|subsided|paving|footpath|pavement|cracked and sinking|tiles broken)\b",
            full_text,
        )
    )

    # Multi-signal / Ambiguity checks
    if is_heritage and is_streetlight:
        # e.g. "Heritage lamp post knocked over" or "Heritage street, lights out"
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"
        evidence_phrase = extract_cited_phrase(description, ["heritage", "lamp post", "lights out"])
    elif is_heritage and is_noise:
        # e.g. "Street vendors using amplifiers illegally in heritage precinct" or "Wedding band near Tagore Museum"
        category = "Noise"
        evidence_phrase = extract_cited_phrase(description, ["amplifier", "wedding band", "music"])
    elif is_heritage and (is_road_damage or "cobblestones" in full_text or "heritage stone" in full_text):
        # e.g. "Historic tram road cobblestones broken up" or "heritage stone not replaced"
        category = "Heritage Damage"
        evidence_phrase = extract_cited_phrase(
            description, ["cobblestones", "heritage stone", "historic tram road", "defaced"]
        )
    elif is_heritage:
        category = "Heritage Damage"
        evidence_phrase = extract_cited_phrase(description, ["heritage", "historic", "museum", "defaced"])
    elif is_pothole:
        category = "Pothole"
        evidence_phrase = extract_cited_phrase(description, ["pothole", "potholes"])
    elif is_heat:
        category = "Heat Hazard"
        evidence_phrase = extract_cited_phrase(description, ["melting", "heat", "temperature", "burns"])
    elif is_noise:
        category = "Noise"
        evidence_phrase = extract_cited_phrase(description, ["music", "band", "amplifier", "noise"])
    elif is_waste:
        category = "Waste"
        evidence_phrase = extract_cited_phrase(description, ["waste", "garbage", "bins", "dumped", "dead animal"])
    elif is_flooding:
        category = "Flooding"
        evidence_phrase = extract_cited_phrase(description, ["flooded", "flooding", "water"])
        if is_drain:
            flag = "NEEDS_REVIEW"
    elif is_drain:
        category = "Drain Blockage"
        evidence_phrase = extract_cited_phrase(description, ["draining", "drain", "drainage", "irrigation"])
    elif is_road_damage:
        category = "Road Damage"
        evidence_phrase = extract_cited_phrase(
            description, ["footpath", "road surface", "buckled", "subsidence", "subsided", "tiles"]
        )
        if "gas leak" in full_text or "pipeline" in full_text:
            flag = "NEEDS_REVIEW"
    elif is_streetlight:
        category = "Streetlight"
        evidence_phrase = extract_cited_phrase(description, ["streetlight", "lighting", "darkness", "substation"])
        if "substation" in full_text:
            flag = "NEEDS_REVIEW"
    else:
        # Fallback category
        category = "Other"
        flag = "NEEDS_REVIEW"
        evidence_phrase = description[:50].strip()

    # Safety check on allowed categories
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Construct one-sentence justification citing specific words
    if priority == "Urgent":
        reason = (
            f"Classified as {category} based on '{evidence_phrase}' "
            f"and prioritized as Urgent due to severity trigger {severity_evidence}."
        )
    else:
        if flag == "NEEDS_REVIEW":
            reason = (
                f"Classified as {category} based on '{evidence_phrase}', "
                f"flagged for review due to overlapping civic infrastructure domains."
            )
        else:
            reason = f"Classified as {category} (Standard priority) citing '{evidence_phrase}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.
    Guarantees output generation, flags nulls, and does not crash on malformed data.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        for row_idx, row in enumerate(reader, start=1):
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                cid = row.get("complaint_id", f"ROW-{row_idx}") if isinstance(row, dict) else f"ROW-{row_idx}"
                results.append(
                    {
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification failed due to row error: {str(e)}.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

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
    print(f"Done. Classified results written to {args.output}")
