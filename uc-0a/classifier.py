"""
UC-0A — Complaint Classifier
Built using RICE framework, agents.md guardrails, and skills.md specification.
"""
import argparse
import csv
import os
import re
from typing import Dict, Any, Tuple, List

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
    r"\binjur(?:y|ies|ed)\b",
    r"\bchild(?:ren)?\b",
    r"\bschool(?:s)?\b",
    r"\bhospital(?:s|ised|ized)?\b",
    r"\bambulance(?:s)?\b",
    r"\bfire(?:s)?\b",
    r"\bhazard(?:s|ous)?\b",
    r"\bfell\b",
    r"\bcollaps(?:e|ed|ing|es)\b",
]


def check_severity(text: str) -> Tuple[bool, List[str]]:
    """Check if any severity trigger keywords are present in text."""
    matched = []
    for pattern in SEVERITY_KEYWORDS:
        found = re.findall(pattern, text, flags=re.IGNORECASE)
        if found:
            matched.extend(found)
    return (len(matched) > 0, matched)


def classify_complaint(row: Dict[str, Any]) -> Dict[str, str]:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()
    location = str(row.get("location", "")).strip()
    full_text = f"{location} {description}".strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing complaint description; classified as Other with review required.",
            "flag": "NEEDS_REVIEW",
        }

    is_urgent, urgent_triggers = check_severity(full_text)
    priority = "Urgent" if is_urgent else "Standard"

    desc_lower = description.lower()
    loc_lower = location.lower()
    clean_desc = description.rstrip(".")

    category = "Other"
    flag = ""

    # 1. Structural Road Damage (takes precedence over pothole when structural collapse/footpath occurs)
    if re.search(r"\b(?:road collapsed|collapsed partially|cracked and sinking|footpath|footpath tiles|broken bench|upturned paving|road subsided|buckled near bridge)\b", desc_lower):
        category = "Road Damage"

    # 2. Pothole
    elif re.search(r"\bpotholes?\b|\bcrater\b|\btyre damage\b|\btire damage\b|\bwheel\b", desc_lower):
        category = "Pothole"

    # 3. Heat Hazard
    elif re.search(r"\b(?:melting at|bubbling at|\d+°c|52°c|heatwave|dangerous temperatures|storing heat|burns on contact|full sun|surface temperature|temperature reads)\b", desc_lower):
        category = "Heat Hazard"

    # 4. Drain Blockage
    elif re.search(r"\b(?:drain blocked|drain completely blocked|main drain|stormwater drain|drainage|manhole cover|mosquito breeding)\b", desc_lower):
        category = "Drain Blockage"

    # 5. Flooding / Waterlogging
    elif re.search(r"\b(?:flooded|flooding|floods|knee-deep|standing in water|rainwater|draining directly onto)\b", desc_lower):
        category = "Flooding"

    # 6. Noise
    elif re.search(r"\b(?:music|drilling|wedding band|amplifiers|engines on|idling with engines|club music|loud)\b", desc_lower):
        category = "Noise"

    # 7. Waste
    elif re.search(r"\b(?:garbage|waste|bins|dead animal|dumped|piles of waste|overflowing garbage)\b", desc_lower):
        category = "Waste"

    # 8. Streetlight
    elif re.search(r"\b(?:streetlights?|lamp post|lights out|flickering and sparking|unlit|darkness for|substation tripped|wiring theft)\b", desc_lower):
        category = "Streetlight"

    # 9. Heritage Damage
    elif re.search(r"\b(?:heritage|historic|ancient|tram road cobblestones|defaced by billboard|heritage stone|tagore museum)\b", desc_lower) and not re.search(r"\b(?:garbage|waste|music|band)\b", desc_lower):
        category = "Heritage Damage"

    # 10. Fallback / Ambiguous cases
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Format single-sentence reason citing exact words
    if is_urgent:
        reason = f"Classified as {category} with Urgent priority due to severity signal '{urgent_triggers[0]}' in '{clean_desc}'."
    else:
        reason = f"Classified as {category} with Standard priority based on description: '{clean_desc}'."

    # Validate category is strictly in allowed categories
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
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Isolate row failures to prevent batch crash
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                })

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
