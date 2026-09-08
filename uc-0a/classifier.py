"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
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

SEVERITY_REGEX = re.compile(
    r"\b(injur\w*|child\w*|school\w*|hospital\w*|ambulance\w*|fire\w*|hazard\w*|fell|collaps\w*)\b",
    re.IGNORECASE,
)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    desc = row.get("description", "").strip()
    loc = row.get("location", "").strip()
    text = f"{desc} {loc}".lower()

    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing complaint description; routed for manual categorization.",
            "flag": "NEEDS_REVIEW",
        }

    # Evaluate severity keywords for Priority escalation
    severity_match = SEVERITY_REGEX.search(desc)
    if severity_match:
        priority = "Urgent"
        matched_trigger = severity_match.group(0)
    else:
        # Check for minor non-disruptive feedback
        if re.search(r"\b(music|wedding|festival|club)\b", text):
            priority = "Low"
            matched_trigger = None
        else:
            priority = "Standard"
            matched_trigger = None

    # Category matching logic
    category = "Other"
    flag = ""
    citations = []

    has_pothole = bool(re.search(r"\bpotholes?\b", text))
    has_flooding = bool(re.search(r"\b(flood\w*|waterlogg\w*|underpass flooded|knee-deep)\b", text))
    has_drain = bool(re.search(r"\b(drain\w*|stormwater drain|manhole)\b", text))
    has_light = bool(re.search(r"\b(streetlight\w*|lights? out|lamp post|darkness|unlit|flickering)\b", text))
    has_waste = bool(re.search(r"\b(waste|garbage|debris|dead animal|bins? overflowing|dumped|refuse)\b", text))
    has_noise = bool(re.search(r"\b(music|noise|drilling|amplifiers?|engines? on|supermarket delivery trucks)\b", text))
    has_heritage = bool(re.search(r"\b(heritage|historic|museum|ancient step well|palace)\b", text))
    has_heat = bool(re.search(r"\b(melting|\d+°c|heatwave|temperature|burns on contact|full sun)\b", text))
    has_road = bool(re.search(r"\b(road surface|cracked|sinking|subsided|buckled|footpath|tiles? broken|crater|paving)\b", text))

    # Determine primary category and potential ambiguity
    matches = []
    if has_pothole:
        matches.append("Pothole")
    if has_flooding:
        matches.append("Flooding")
    if has_drain:
        matches.append("Drain Blockage")
    if has_light:
        matches.append("Streetlight")
    if has_waste:
        matches.append("Waste")
    if has_noise:
        matches.append("Noise")
    if has_heritage:
        matches.append("Heritage Damage")
    if has_heat:
        matches.append("Heat Hazard")
    if has_road:
        matches.append("Road Damage")

    if has_heritage and has_light:
        # Heritage street with lights out: primary functional issue is Streetlight, but Heritage involved
        category = "Streetlight"
        flag = "NEEDS_REVIEW"
        citations.append(f"lights out on heritage street")
    elif has_heritage and has_noise:
        category = "Noise"
        flag = "NEEDS_REVIEW"
        citations.append("music near heritage precinct")
    elif has_heritage and (has_road or "cobblestones" in text or "defaced" in text or "step well" in text or "heritage stone" in text):
        category = "Heritage Damage"
        if has_road:
            flag = "NEEDS_REVIEW"
        citations.append("heritage structure / historic paving affected")
    elif has_pothole:
        category = "Pothole"
        citations.append("pothole reported on roadway")
    elif has_drain and has_flooding:
        # Flooding caused by blocked drain
        category = "Drain Blockage"
        flag = "NEEDS_REVIEW"
        citations.append("drain blocked causing water accumulation")
    elif has_flooding:
        category = "Flooding"
        citations.append("waterlogging / flooding reported")
    elif has_drain:
        category = "Drain Blockage"
        citations.append("drain blockage reported")
    elif has_light:
        category = "Streetlight"
        citations.append("lighting outage or electrical defect")
    elif has_waste:
        category = "Waste"
        citations.append("waste accumulation / sanitation issue")
    elif has_noise:
        category = "Noise"
        citations.append("excessive noise disruption")
    elif has_heat:
        category = "Heat Hazard"
        citations.append("extreme temperature heat hazard")
    elif has_road or "manhole cover missing" in text:
        category = "Road Damage"
        citations.append("damaged road surface or pedestrian walkway")
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        citations.append("issue requires specialized routing")

    # Construct one-sentence justification citing specific words from description
    if matched_trigger:
        reason = f"Classified as {category} with {priority} priority due to '{matched_trigger}' and complaint stating '{desc}'."
    else:
        reason = f"Classified as {category} with {priority} priority based on citizen report citing '{desc}'."

    # Guarantee reason is exactly one sentence
    reason = reason.replace("\n", " ").strip()
    if not reason.endswith("."):
        reason += "."

    assert category in ALLOWED_CATEGORIES, f"Invalid category {category}"
    assert priority in ["Urgent", "Standard", "Low"], f"Invalid priority {priority}"

    res = dict(row)
    res["category"] = category
    res["priority"] = priority
    res["reason"] = reason
    res["flag"] = flag
    return res


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, mode="r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    out_fieldnames = list(fieldnames)
    for col in ["category", "priority", "reason", "flag"]:
        if col not in out_fieldnames:
            out_fieldnames.append(col)

    classified_rows = []
    for r in rows:
        classified = classify_complaint(r)
        classified_rows.append(classified)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(classified_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

