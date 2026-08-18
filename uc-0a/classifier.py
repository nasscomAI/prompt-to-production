"""
UC-0A — Complaint Classifier
Implements the RICE specification from agents.md and skills.md.
"""
import argparse
import csv
import re
from typing import Dict, Any, Tuple, Optional

# Strict 10-category taxonomy
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
    r"\binjur(?:y|ies|ed)?\b",
    r"\bchild(?:ren)?\b",
    r"\bschool(?:s)?\b",
    r"\bhospital(?:s|ised|ized)?\b",
    r"\bambulance(?:s)?\b",
    r"\bfire(?:s)?\b",
    r"\bhazard(?:s)?\b",
    r"\bfell\b",
    r"\bcollapse(?:d|s|ing)?\b",
]

SEVERITY_PATTERN = re.compile("|".join(SEVERITY_KEYWORDS), re.IGNORECASE)


def detect_severity(text: str) -> Tuple[str, Optional[str]]:
    """
    Checks if text contains severity triggers for Urgent priority.
    Returns (priority, matched_keyword).
    """
    match = SEVERITY_PATTERN.search(text)
    if match:
        return "Urgent", match.group(0)
    return "Standard", None


def determine_category(description: str, location: str) -> Tuple[str, str, bool]:
    """
    Determines category and extracted justification quote from description and location.
    Returns: (category, key_evidence, is_ambiguous)
    """
    desc_clean = description.strip()
    full_text = f"{location} {desc_clean}".lower()
    text = desc_clean.lower()

    if not desc_clean:
        return "Other", "no description provided", True

    # 1. Noise
    if re.search(r"\b(music|drilling|band|amplifier|amplifiers|engines? on|idling|noise|loud)\b", text):
        match = re.search(r"[^.?!;]*(?:music|drilling|band|amplifier|amplifiers|engines? on|idling|noise|loud)[^.?!;]*", desc_clean, re.IGNORECASE)
        quote = match.group(0).strip() if match else desc_clean
        return "Noise", quote, False

    # 2. Heat Hazard
    if re.search(r"(?:°c|\b\d+°?c\b|heatwave|heat\b|temperature|temperatures|melting|bubbling|burns on contact|full sun)", text):
        match = re.search(r"[^.?!;]*(?:°c|\b\d+°?c\b|heatwave|heat\b|temperature|temperatures|melting|bubbling|burns on contact|full sun)[^.?!;]*", desc_clean, re.IGNORECASE)
        quote = match.group(0).strip() if match else desc_clean
        return "Heat Hazard", quote, False

    # 3. Heritage Damage (Physical / Structural / Aesthetic damage to heritage assets)
    if re.search(r"\b(heritage|historic|ancient|monument|tagore museum|step well)\b", full_text) and \
       re.search(r"\b(lamp post|cobblestone|cobblestones|building|defaced|stone|paving|damage|subsidence|knocked over)\b", text):
        match = re.search(r"[^.?!;]*(?:heritage|historic|ancient|cobblestone|defaced|stone|step well|lamp post)[^.?!;]*", desc_clean, re.IGNORECASE)
        quote = match.group(0).strip() if match else desc_clean
        return "Heritage Damage", quote, False

    # 4. Pothole
    if re.search(r"\b(pothole|potholes|crater)\b", text) and not re.search(r"\b(road collapsed|surface cracked)\b", text):
        match = re.search(r"[^.?!;]*(?:pothole|potholes|crater)[^.?!;]*", desc_clean, re.IGNORECASE)
        quote = match.group(0).strip() if match else desc_clean
        return "Pothole", quote, False

    # 5. Drain Blockage
    if re.search(r"\b(drain|drains|drainage|stormwater|manhole|draining directly|mosquito breeding|dengue)\b", text):
        match = re.search(r"[^.?!;]*(?:drain|drains|drainage|stormwater|manhole|draining|mosquito|dengue)[^.?!;]*", desc_clean, re.IGNORECASE)
        quote = match.group(0).strip() if match else desc_clean
        return "Drain Blockage", quote, False

    # 6. Flooding
    if re.search(r"\b(flood|floods|flooded|flooding|knee-deep|waterlogging|under water|standing in water|rainwater)\b", text):
        match = re.search(r"[^.?!;]*(?:flood|floods|flooded|flooding|knee-deep|waterlogging|water|rainwater)[^.?!;]*", desc_clean, re.IGNORECASE)
        quote = match.group(0).strip() if match else desc_clean
        return "Flooding", quote, False

    # 7. Streetlight
    if re.search(r"\b(streetlight|streetlights|lights out|unlit|darkness|dark at night|sparking|flickering|substation tripped|lamp post)\b", text):
        match = re.search(r"[^.?!;]*(?:streetlight|streetlights|lights out|unlit|darkness|dark|sparking|flickering|substation|lamp post)[^.?!;]*", desc_clean, re.IGNORECASE)
        quote = match.group(0).strip() if match else desc_clean
        return "Streetlight", quote, False

    # 8. Waste
    if re.search(r"\b(garbage|waste|bins?|dumped|dead animal|litter|trash|carcass)\b", text):
        match = re.search(r"[^.?!;]*(?:garbage|waste|bins?|dumped|dead animal|litter|trash|carcass)[^.?!;]*", desc_clean, re.IGNORECASE)
        quote = match.group(0).strip() if match else desc_clean
        return "Waste", quote, False

    # 9. Road Damage
    if re.search(r"\b(road surface|surface cracked|footpath|tiles broken|sinking|subsidence|subsided|buckled|collapsed|crater|paving|road collapsed|road subsided)\b", text):
        match = re.search(r"[^.?!;]*(?:road surface|surface|footpath|tiles|sinking|subsidence|subsided|buckled|collapsed|paving)[^.?!;]*", desc_clean, re.IGNORECASE)
        quote = match.group(0).strip() if match else desc_clean
        return "Road Damage", quote, False

    # 10. Fallback / Ambiguous -> Other
    return "Other", desc_clean[:60] if desc_clean else "unspecified description", True


def classify_complaint(row: Dict[str, Any]) -> Dict[str, str]:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    location = row.get("location", "").strip()

    # Determine priority via severity triggers
    combined_text = f"{description} {location}".strip()
    priority, severity_match = detect_severity(combined_text)

    # Determine category
    category, evidence, is_ambiguous = determine_category(description, location)

    # Format one-sentence reason citing explicit words from description
    evidence_snippet = evidence.strip().rstrip(".")
    if not description:
        reason = "Missing complaint description; classified as Other with review flag."
        flag = "NEEDS_REVIEW"
        category = "Other"
    elif priority == "Urgent":
        reason = f"Urgent priority triggered by severity signal '{severity_match}'; categorized as {category} based on '{evidence_snippet}'."
        flag = "NEEDS_REVIEW" if (is_ambiguous or category == "Other") else ""
    else:
        reason = f"Categorized as {category} based on '{evidence_snippet}'."
        flag = "NEEDS_REVIEW" if (is_ambiguous or category == "Other") else ""

    # Enforce allowed category enum strictly
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
    Handles nulls and errors safely without crashing.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Safe recovery on malformed row
                cid = row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN"
                results.append({
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                })

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

