"""
UC-0A — Complaint Classifier
Vibe-coded and CRAFT-tested civic complaint classification tool.
"""
import argparse
import csv
import re
from typing import Dict, Optional, Tuple

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

# Regex patterns for severity triggers (including word variations like children, hospitalised, collapsed)
SEVERITY_PATTERN = re.compile(
    r"\b(injur(?:y|ies|ed)|child(?:ren)?|school(?:s)?|hospital(?:ised|ized)?|ambulance(?:s)?|fire(?:s)?|hazard(?:s|ous)?|fell|collaps(?:e|ed|ing))\b",
    re.IGNORECASE,
)


def _extract_quoted_evidence(description: str, keywords: list) -> str:
    """Extract a short snippet containing the key evidence words."""
    desc_lower = description.lower()
    for kw in keywords:
        pos = desc_lower.find(kw)
        if pos != -1:
            # Try to grab the clause or sentence
            start = max(0, description.rfind(".", 0, pos) + 1)
            end = description.find(".", pos)
            if end == -1:
                end = len(description)
            snippet = description[start:end].strip()
            if snippet:
                return snippet
    # Fallback to the first sentence or up to 60 chars
    first_sentence = description.split(".")[0].strip()
    return first_sentence[:60] if first_sentence else description[:60]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    location = row.get("location", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty; unable to determine category.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()
    loc_lower = location.lower()
    full_text = f"{desc_lower} {loc_lower}"

    # 1. Determine Priority via Severity Triggers
    severity_match = SEVERITY_PATTERN.search(description)
    is_urgent = severity_match is not None
    priority = "Urgent" if is_urgent else "Standard"

    # 2. Determine Category
    category = "Other"
    flag = ""
    evidence_terms = []

    # Check Pothole
    if re.search(r"\bpotholes?\b", full_text):
        category = "Pothole"
        evidence_terms = ["pothole", "potholes"]
    # Check Drain Blockage (takes precedence if drain/manhole is specifically blocked or missing)
    elif re.search(r"\b(drain\s+(?:is\s+)?blocked|drainage|stormwater drain|main drain|drain blocked|manhole)\b", full_text):
        category = "Drain Blockage"
        evidence_terms = ["drain", "blocked", "manhole"]
    # Check Flooding
    elif re.search(r"\b(flood(?:ed|ing|s)?|waterlogging|underpass flooded|inundat)\b", full_text):
        category = "Flooding"
        evidence_terms = ["flood", "flooded", "flooding", "water"]
    # Check Streetlight
    elif re.search(r"\b(streetlight|streetlights|lamp\s*post|unlit|darkness|lights out|flickering|sparking)\b", full_text):
        category = "Streetlight"
        evidence_terms = ["streetlight", "lights out", "dark", "unlit", "sparking", "flickering"]
    # Check Waste
    elif re.search(r"\b(garbage|waste|dead animal|bins overflowing|overflowing garbage|dumped)\b", full_text):
        category = "Waste"
        evidence_terms = ["garbage", "waste", "animal", "dumped", "bins"]
    # Check Noise
    elif re.search(r"\b(music|wedding venue|wedding band|drilling|amplifiers|loud|noise|engines on|subwoofer)\b", full_text):
        category = "Noise"
        evidence_terms = ["music", "drilling", "amplifiers", "noise"]
    # Check Heritage Damage
    elif (
        re.search(r"\b(heritage|historic|ancient)\b", full_text)
        and re.search(r"\b(defaced|billboard|stone not replaced|cobblestones|monument|step well)\b", full_text)
    ):
        category = "Heritage Damage"
        evidence_terms = ["heritage", "historic", "defaced", "stone"]
    # Check Heat Hazard
    elif re.search(r"\b(melting at|\b\d{2}°c\b|dangerous temperatures|heatwave|surface temperature|storing heat|burns on contact|full sun)\b", full_text):
        category = "Heat Hazard"
        evidence_terms = ["melting", "°C", "temperatures", "heat", "heatwave", "burns"]
    # Check Road Damage
    elif re.search(r"\b(road surface|road collapsed|cracked|sinking|subsidence|buckled|footpath|tiles broken|paving|crater)\b", full_text):
        category = "Road Damage"
        evidence_terms = ["road surface", "footpath", "sinking", "cracked", "tiles broken", "collapsed", "subsidence"]
    else:
        # Ambiguous complaint or unsupported domain (e.g. tree cutting, electrical substation)
        category = "Other"
        flag = "NEEDS_REVIEW"
        evidence_terms = ["unspecified"]

    # 3. Formulate Reason (citing verbatim words from the description)
    matched_words = [w for w in evidence_terms if w in desc_lower]
    if severity_match:
        trigger_word = severity_match.group(0)
        reason_evidence = f'"{trigger_word}"'
    elif matched_words:
        reason_evidence = f'"{matched_words[0]}"'
    else:
        evidence_snippet = _extract_quoted_evidence(description, evidence_terms)
        reason_evidence = f'"{evidence_snippet}"'

    if flag == "NEEDS_REVIEW":
        reason = f'Category is ambiguous based on "{description[:50]}" and flagged for manual review.'
    elif is_urgent:
        reason = f'Classified as {category} with Urgent priority due to safety signal {reason_evidence} in description.'
    else:
        reason = f'Classified as {category} with Standard priority based on {reason_evidence} in description.'

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> int:
    """
    Read input CSV, classify each row, and write results CSV.
    Guarantees: handles nulls, does not crash on malformed rows, and enforces schema.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    processed_count = 0

    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        rows_to_write = []
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as e:
                classified = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification error: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                }
            rows_to_write.append(classified)
            processed_count += 1

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_write)

    return processed_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    count = batch_classify(args.input, args.output)
    print(f"Done. Processed {count} complaints. Results written to {args.output}")
