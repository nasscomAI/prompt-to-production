"""
UC-0A — Complaint Classifier
Deterministic, offline rule-based classifier obeying RICE specification from agents.md and skills.md.
"""
import argparse
import csv
import re
from typing import Dict, List, Tuple

# Allowed taxonomy values
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

# Severity triggers that MUST trigger Urgent priority
SEVERITY_TRIGGERS = [
    (r"\binjur(?:y|ies|ed)?\b", "injury"),
    (r"\bchild(?:ren)?\b", "child"),
    (r"\bschool(?:s)?\b", "school"),
    (r"\bhospital(?:s|ised|ized)?\b", "hospital"),
    (r"\bambulance(?:s)?\b", "ambulance"),
    (r"\bfire(?:s)?\b", "fire"),
    (r"\bhazard(?:s|ous)?\b", "hazard"),
    (r"\bfell\b", "fell"),
    (r"\bcollaps(?:e|ed|ing|es)?\b", "collapse"),
]


def _detect_severity(description: str) -> Tuple[str, List[str]]:
    """Check for presence of severity trigger keywords."""
    if not description:
        return "Standard", []
    
    matched_triggers = []
    for pattern, _ in SEVERITY_TRIGGERS:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            matched_triggers.append(match.group(0))
            
    if matched_triggers:
        return "Urgent", matched_triggers
    return "Standard", []


def _detect_category(description: str) -> Tuple[str, str, bool]:
    """
    Determine category, justification keywords, and ambiguity status.
    Returns: (category, matched_phrase, is_ambiguous)
    """
    if not description or not description.strip():
        return "Other", "missing description", True

    desc_lower = description.lower()

    # 1. Pothole
    m = re.search(r"\bpotholes?\b", description, re.IGNORECASE)
    if m:
        return "Pothole", m.group(0), False

    # 2. Drain Blockage (check before flooding if drain explicitly mentioned as root cause)
    m = re.search(r"\b(?:drain(?:age)?\s+(?:is\s+)?(?:completely\s+)?blocked|stormwater\s+drain(?:\s+100%\s+blocked)?|main\s+drain\s+blocked|drain\s+blocked|blocked\s+drain|drainage\s+blocked)\b", description, re.IGNORECASE)
    if m:
        return "Drain Blockage", m.group(0), False

    # 3. Flooding
    m = re.search(r"\b(?:flood(?:s|ed|ing)?|channel\s+rainwater|waterlogging|waterlogged|submerged|knee-deep)\b", description, re.IGNORECASE)
    if m:
        return "Flooding", m.group(0), False

    # 4. Noise
    m = re.search(r"\b(?:music|drilling|amplifiers?|wedding\s+band|engines?\s+on|idling\s+with\s+engines|loud\s+noise|decibels?)\b", description, re.IGNORECASE)
    if m:
        return "Noise", m.group(0), False

    # 5. Waste
    m = re.search(r"\b(?:garbage(?:\s+overflow)?|waste|bins?\s+overflowing|overflowing\s+garbage|dead\s+animal|dumped\s+on\s+public\s+road|piles\s+of\s+waste|litter|debris)\b", description, re.IGNORECASE)
    if m:
        return "Waste", m.group(0), False

    # 6. Streetlight
    m = re.search(r"\b(?:streetlights?|street\s+lights?|lights?\s+out|unlit|darkness|substation\s+tripped|sparking|wiring\s+theft)\b", description, re.IGNORECASE)
    if m:
        return "Streetlight", m.group(0), False

    # 7. Heat Hazard
    m = re.search(r"\b(?:(?:tarmac\s+surface\s+)?melting|heatwave(?:\s+conditions)?|dangerous\s+temperatures?|surface\s+bubbling|\d+°\s*c|temperature\s+unbearable|storing\s+heat|burns?\s+on\s+contact|full\s+sun)\b", description, re.IGNORECASE)
    if m:
        return "Heat Hazard", m.group(0), False

    # 8. Heritage Damage
    m = re.search(r"\b(?:heritage\s+(?:lamp\s+post|stone|building|residential|concern|area|precinct)|historic\s+tram(?:\s+road\s+cobblestones)?|cobblestones?\s+broken|monument|ancient\s+step\s*well|defaced\s+by\s+billboard)\b", description, re.IGNORECASE)
    if m:
        return "Heritage Damage", m.group(0), False

    # 9. Road Damage
    m = re.search(r"\b(?:road\s+(?:surface\s+)?(?:collapsed|cracked|subsidence|sinking|surface\s+buckled)|road\s+subsided|footpath\s+(?:broken|sinking|tiles\s+broken)|upturned\s+paving|manhole\s+cover\s+missing|crater(?:\s+\d+m\s+deep)?)\b", description, re.IGNORECASE)
    if m:
        return "Road Damage", m.group(0), False

    # Residual / Ambiguous cases
    m = re.search(r"\b(?:draining(?:\s+directly\s+onto\s+public\s+road)?|rainwater|water)\b", description, re.IGNORECASE)
    if m:
        return "Drain Blockage", m.group(0), True

    m = re.search(r"\b(?:trees?|irrigation|gas\s+leak)\b", description, re.IGNORECASE)
    if m:
        return "Other", m.group(0), True

    return "Other", "unrecognized civic description", True


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        return {
            "complaint_id": "UNKNOWN",
            "category": "Other",
            "priority": "Standard",
            "reason": "Malformed or non-dictionary input record.",
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = str(row.get("complaint_id", "") or "").strip()
    if not complaint_id:
        complaint_id = "UNKNOWN"

    description = str(row.get("description", "") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty complaint description.",
            "flag": "NEEDS_REVIEW",
        }

    # Determine severity
    priority, severity_triggers = _detect_severity(description)

    # Determine category
    category, matched_phrase, is_ambiguous = _detect_category(description)

    # Validate category against allowed list
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        is_ambiguous = True

    # Construct one-sentence reason citing exact words
    if priority == "Urgent":
        triggers_str = ", ".join(f"'{t}'" for t in set(severity_triggers))
        reason = (
            f"Classified as {category} based on '{matched_phrase}'; "
            f"escalated to Urgent due to severity trigger(s) {triggers_str}."
        )
    else:
        reason = (
            f"Classified as {category} based on description keyword '{matched_phrase}'; "
            f"priority set to Standard with no emergency safety triggers detected."
        )

    # Set flag
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    try:
        with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    cid = row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN"
                    results.append({
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW",
                    })
    except Exception as e:
        print(f"Error opening or reading input file {input_path}: {e}")
        return

    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing results to {output_path}: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
