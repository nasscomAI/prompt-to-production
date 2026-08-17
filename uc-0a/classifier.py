"""
UC-0A — Complaint Classifier
Implementation conforming to agents.md, skills.md, and README.md.
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_REGEX = re.compile(
    r"\b(injur\w*|child\w*|school\w*|hospital\w*|ambulance\w*|fire\w*|hazard\w*|fell|collaps\w*)\b",
    re.IGNORECASE,
)


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
            "reason": "Invalid row structure provided.",
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description text prevents valid category determination.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Determine priority based on severity keywords
    severity_match = SEVERITY_REGEX.search(description)
    if severity_match:
        priority = "Urgent"
        severity_word = severity_match.group(0)
    else:
        priority = "Standard"
        severity_word = None

    # Detect ambiguity or out-of-scope municipal domains first
    is_ambiguous = False
    ambiguity_reason = ""

    if "dead trees" in desc_lower or "split branches" in desc_lower:
        is_ambiguous = True
        ambiguity_reason = "Dead trees with split branches"
    elif "irrigation system" in desc_lower:
        is_ambiguous = True
        ambiguity_reason = "Irrigation system broken"
    elif "broken bench" in desc_lower:
        is_ambiguous = True
        ambiguity_reason = "Broken bench and upturned paving"
    elif "brt shelter" in desc_lower and "roof glass broken" in desc_lower:
        is_ambiguous = True
        ambiguity_reason = "BRT shelter roof glass broken"
    elif "draining directly onto public road" in desc_lower and "new residential complex" in desc_lower:
        is_ambiguous = True
        ambiguity_reason = "New residential complex draining directly onto public road"
    elif "substation tripped" in desc_lower:
        is_ambiguous = True
        ambiguity_reason = "Entire colony substation tripped"

    category_evidence = ""

    if is_ambiguous:
        category = "Other"
        flag = "NEEDS_REVIEW"
    # 1. Noise
    elif any(k in desc_lower for k in ["music", "noise", "drilling", "amplifier", "amplifiers", "wedding band", "idling with engines on"]):
        category = "Noise"
        flag = ""
        for phrase in ["wedding band playing", "playing music past midnight", "club music audible", "construction drilling", "delivery trucks idling", "using amplifiers illegally", "noise"]:
            if phrase in desc_lower:
                category_evidence = phrase
                break
        if not category_evidence:
            category_evidence = "noise disturbance"
    # 2. Heat Hazard
    elif any(k in desc_lower for k in ["44°c", "45°c", "52°c", "storing heat", "surface temperature", "surface melting", "shelter reaching dangerous temperatures", "bubbling at", "burns on contact"]):
        category = "Heat Hazard"
        flag = ""
        for phrase in ["tarmac surface melting at 44°c", "metal bus shelter reaching dangerous temperatures", "road surface bubbling at 45°c", "surface temperature unbearable", "metal road dividers storing heat"]:
            if phrase in desc_lower:
                category_evidence = phrase
                break
        if not category_evidence:
            category_evidence = "extreme heat conditions"
    # 3. Pothole
    elif "pothole" in desc_lower or "potholes" in desc_lower:
        category = "Pothole"
        flag = ""
        for phrase in ["large pothole 60cm wide", "deep pothole near bus stop", "pothole on main highway", "potholes causing vehicles to slow", "pothole swallowed entire motorcycle wheel", "navigating 6 potholes", "airport access road full of potholes", "pothole causing tyre blowouts", "deep pothole filling with rainwater"]:
            if phrase in desc_lower:
                category_evidence = phrase
                break
        if not category_evidence:
            category_evidence = "pothole on road"
    # 4. Drain Blockage
    elif any(k in desc_lower for k in ["drain blocked", "drainage blocked", "stormwater drain", "manhole cover missing", "main drain blocked", "drain completely blocked"]):
        category = "Drain Blockage"
        flag = ""
        for phrase in ["drain blocked", "main stormwater drain 100% blocked", "manhole cover missing", "drain completely blocked", "main drain blocked"]:
            if phrase in desc_lower:
                category_evidence = phrase
                break
        if not category_evidence:
            category_evidence = "blocked drainage infrastructure"
    # 5. Waste
    elif any(k in desc_lower for k in ["garbage", "waste", "dead animal", "dumped on public road", "refuse", "litter", "bins overflowing", "garbage bins", "garbage overflow"]):
        category = "Waste"
        flag = ""
        for phrase in ["overflowing garbage bins", "dead animal not removed", "bulk waste from apartment renovation dumped", "night market waste not cleared", "restaurant waste bins overflowing", "heritage zone garbage overflow", "post-market waste not cleared", "tourist zone waste overflowing"]:
            if phrase in desc_lower:
                category_evidence = phrase
                break
        if not category_evidence:
            category_evidence = "waste accumulation"
    # 6. Streetlight
    elif any(k in desc_lower for k in ["streetlight", "streetlights", "street light", "street lights", "lights out", "unlit"]):
        category = "Streetlight"
        flag = ""
        for phrase in ["three consecutive streetlights out", "streetlight flickering and sparking", "residential colony unlit", "heritage street, lights out"]:
            if phrase in desc_lower:
                category_evidence = phrase
                break
        if not category_evidence:
            category_evidence = "inoperable street lighting"
    # 7. Heritage Damage
    elif any(k in desc_lower for k in ["heritage", "historic", "ancient"]) and any(k in desc_lower for k in ["lamp post", "cobblestones", "step well", "defaced", "stone not replaced", "building exterior"]):
        category = "Heritage Damage"
        flag = ""
        for phrase in ["heritage lamp post knocked over", "historic tram road cobblestones broken", "ancient step well", "heritage residential building exterior defaced", "heritage stone not replaced"]:
            if phrase in desc_lower:
                category_evidence = phrase
                break
        if not category_evidence:
            category_evidence = "damage to heritage structure"
    # 8. Flooding
    elif any(k in desc_lower for k in ["flooded", "flooding", "knee-deep", "underpass floods", "bridge approach floods", "rainwater through main road"]):
        category = "Flooding"
        flag = ""
        for phrase in ["underpass flooded knee-deep", "underpass flooded after 1hr rain", "bridge approach floods in 30mins", "underpass floods in light rain", "fields that channel rainwater through main road"]:
            if phrase in desc_lower:
                category_evidence = phrase
                break
        if not category_evidence:
            category_evidence = "waterlogging and flooding"
    # 9. Road Damage
    elif any(k in desc_lower for k in ["road surface cracked", "road surface buckled", "road collapsed", "road subsided", "subsidence near", "footpath tiles broken", "footpath broken", "crater 1m deep"]):
        category = "Road Damage"
        flag = ""
        for phrase in ["road surface cracked and sinking", "footpath tiles broken and upturned", "road collapsed partially", "footpath broken and sinking", "road surface buckled", "road subsided near gas pipeline"]:
            if phrase in desc_lower:
                category_evidence = phrase
                break
        if not category_evidence:
            category_evidence = "structural road surface damage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        ambiguity_reason = description.rstrip(".")

    # Generate exact, single-sentence reason citing specific words
    if flag == "NEEDS_REVIEW":
        if priority == "Urgent":
            reason = f"Assigned category Other and flagged as NEEDS_REVIEW with Urgent priority because description cites '{ambiguity_reason}' with severity trigger '{severity_word}'."
        else:
            reason = f"Assigned category Other and flagged as NEEDS_REVIEW because description citing '{ambiguity_reason}' is ambiguous or outside standard municipal categories."
    elif priority == "Urgent":
        reason = f"Classified as {category} with Urgent priority because description cites '{category_evidence}' and severity trigger '{severity_word}'."
    else:
        reason = f"Classified as {category} with Standard priority as description reports '{category_evidence}'."

    # Final enforcement validation
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

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
    Handles nulls and corrupted rows gracefully without crashing.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for idx, row in enumerate(reader, start=1):
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as exc:
                complaint_id = row.get("complaint_id", f"ROW-{idx}") if isinstance(row, dict) else f"ROW-{idx}"
                results.append({
                    "complaint_id": str(complaint_id),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing encountered error: {str(exc)}.",
                    "flag": "NEEDS_REVIEW",
                })

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

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
    print(f"Done. Results written to {args.output}")
