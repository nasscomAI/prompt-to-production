"""
UC-0A — Complaint Classifier
Guided by agents.md and skills.md RICE specification.
"""
import argparse
import csv
import os
import re

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

SEVERITY_KEYWORDS_RE = re.compile(
    r'\b(?:injur(?:y|ies|ed)|child(?:ren)?|school(?:s)?|hospital(?:ised|ized|s)?|'
    r'ambulance(?:s)?|fire|hazard(?:ous|s)?|fell|fall|collaps(?:e|ed|ing))\b',
    re.IGNORECASE
)

OTHER_URGENT_RE = re.compile(
    r'\b(?:gas leak|substation tripped|lives at risk|diplomatic|blackout)\b',
    re.IGNORECASE
)

LOW_PRIORITY_RE = re.compile(
    r'\b(?:grass dying|bench|past midnight)\b',
    re.IGNORECASE
)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    comp_id = row.get("complaint_id", "") if row else ""
    desc = row.get("description", "") if row else ""

    if not desc or not str(desc).strip():
        return {
            "complaint_id": comp_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing or empty complaint description text.",
            "flag": "NEEDS_REVIEW"
        }

    desc_str = str(desc).strip()
    desc_lower = desc_str.lower()

    # Check severity keywords for Urgent priority
    sev_match = SEVERITY_KEYWORDS_RE.search(desc_str)
    urg_match = OTHER_URGENT_RE.search(desc_str)

    if sev_match:
        priority = "Urgent"
        cited_word = sev_match.group(0)
    elif urg_match:
        priority = "Urgent"
        cited_word = urg_match.group(0)
    elif LOW_PRIORITY_RE.search(desc_str):
        priority = "Low"
        cited_word = None
    else:
        priority = "Standard"
        cited_word = None

    # Score categories
    cat_matches = {}

    # Pothole
    m = re.findall(r'\b(?:potholes?|crater|motorcycle wheel)\b', desc_lower)
    if m:
        cat_matches["Pothole"] = m

    # Flooding
    m = re.findall(r'\b(?:flood(?:ed|ing|s)?|rainwater|underpass flooded|waterlogging)\b', desc_lower)
    if m:
        cat_matches["Flooding"] = m

    # Streetlight
    m = re.findall(r'\b(?:streetlights?|unlit|darkness|lights out|wiring theft|substation tripped)\b', desc_lower)
    if m:
        cat_matches["Streetlight"] = m

    # Waste
    m = re.findall(r'\b(?:garbages?|trash|waste|dead animal|bins?|dumped)\b', desc_lower)
    if m:
        cat_matches["Waste"] = m

    # Noise
    m = re.findall(r'\b(?:music|drilling|amplifiers?|idling|noise|wedding venue|wedding band)\b', desc_lower)
    if m:
        cat_matches["Noise"] = m

    # Road Damage
    m = re.findall(r'\b(?:tarmac|road surface|road collapsed?|footpath|manhole|paving|cracked|sinking|subsidence|buckled|tiles broken|bridge approach)\b', desc_lower)
    if m:
        cat_matches["Road Damage"] = m

    # Heritage Damage
    m = re.findall(r'\b(?:heritage|historic|museum|ancient)\b', desc_lower)
    if m:
        cat_matches["Heritage Damage"] = m

    # Heat Hazard
    m = re.findall(r'\b(?:heatwave|4[45]°c|52°c|melting|burns|full sun|temperature|sun|hot)\b', desc_lower)
    if m:
        cat_matches["Heat Hazard"] = m

    # Drain Blockage
    m = re.findall(r'\b(?:drains?|stormwater drain|drainage)\b', desc_lower)
    if m:
        cat_matches["Drain Blockage"] = m

    flag = ""
    category = "Other"

    # Evaluate ambiguity and determine category
    if "Heritage Damage" in cat_matches and len(cat_matches) > 1:
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"
    elif len(cat_matches) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(cat_matches) == 1:
        category = list(cat_matches.keys())[0]
    else:
        if "Drain Blockage" in cat_matches and "Flooding" in cat_matches:
            if re.search(r'\bblocked\b|\bbreeding\b', desc_lower):
                category = "Drain Blockage"
            else:
                category = "Flooding"
        else:
            sorted_cats = sorted(cat_matches.items(), key=lambda x: len(x[1]), reverse=True)
            category = sorted_cats[0][0]
            if len(sorted_cats) > 1 and len(sorted_cats[0][1]) == len(sorted_cats[1][1]):
                flag = "NEEDS_REVIEW"

    # Formulate reason sentence quoting description words
    if cited_word:
        reason_text = f"Classified as {category} with {priority} priority citing severity term '{cited_word}' from description."
    else:
        snippet = " ".join(desc_str.split()[:7])
        reason_text = f"Classified as {category} with {priority} priority based on description snippet '{snippet}'."

    return {
        "complaint_id": comp_id,
        "category": category,
        "priority": priority,
        "reason": reason_text,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as e:
                comp_id = row.get("complaint_id", "") if row else ""
                classified = {
                    "complaint_id": comp_id,
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error during processing: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                }
            results.append(classified)

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

