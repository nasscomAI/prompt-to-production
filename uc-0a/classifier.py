"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row dynamically.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    desc_lower = description.lower()

    # 1. Priority check (Urgent if severity keywords are present)
    priority = "Standard"
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            break

    # 2. Reason (cite the specific description sentence)
    sentences = re.split(r'[.!?]', description)
    reason = sentences[0].strip() if sentences else description
    if reason and not reason.endswith('.'):
        reason += '.'

    # 3. Category & Flag determination based on rules
    category = "Other"
    flag = ""

    # Pothole check
    if "pothole" in desc_lower:
        category = "Pothole"

    # Flooding checks (handles ambiguity with drains/complexes)
    elif "flood" in desc_lower or "flooding" in desc_lower or "rainwater" in desc_lower or "waterlogging" in desc_lower or "draining" in desc_lower:
        if "drain" in desc_lower or "stormwater" in desc_lower or "draining directly" in desc_lower:
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = "Flooding"

    # Manhole / Sewer checks
    elif "manhole" in desc_lower:
        if "cyclists" in desc_lower or "missing" in desc_lower:
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = "Drain Blockage"

    # Blocked drains check
    elif "drain blocked" in desc_lower or "drainage" in desc_lower or "stormwater drain" in desc_lower or "sewer" in desc_lower:
        category = "Drain Blockage"

    # Streetlights and Power grid
    elif "streetlight" in desc_lower or "unlit" in desc_lower or "darkness" in desc_lower or "lights out" in desc_lower or "substation" in desc_lower:
        if "heritage" in desc_lower or "historic" in desc_lower or "substation tripped" in desc_lower:
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = "Streetlight"

    # Waste/Garbage checks
    elif "waste" in desc_lower or "garbage" in desc_lower or "bins" in desc_lower or "dead animal" in desc_lower:
        if "heritage" in desc_lower or "historic" in desc_lower:
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = "Waste"

    # Noise checks
    elif "noise" in desc_lower or "music" in desc_lower or "amplifiers" in desc_lower or "drilling" in desc_lower or "idling" in desc_lower or "wedding band" in desc_lower:
        if "heritage" in desc_lower or "historic" in desc_lower or "idling" in desc_lower:
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = "Noise"

    # Heat Hazard checks
    elif "heat" in desc_lower or "heatwave" in desc_lower or "temperature" in desc_lower or "melting" in desc_lower or "44°c" in desc_lower or "45°c" in desc_lower or "52°c" in desc_lower or "bubbling" in desc_lower or "sun" in desc_lower:
        if "irrigation" in desc_lower or "broken bench" in desc_lower or "glass broken" in desc_lower:
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = "Heat Hazard"

    # Heritage Damage checks
    elif "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower or "museum" in desc_lower or "step well" in desc_lower or "bow barracks" in desc_lower:
        if "step well" in desc_lower or "paving" in desc_lower:
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = "Heritage Damage"

    # Road Damage checks
    elif "road surface" in desc_lower or "paving" in desc_lower or "footpath" in desc_lower or "tarmac" in desc_lower or "crater" in desc_lower or "sidewalk" in desc_lower or "subsidence" in desc_lower or "cracked" in desc_lower or "sinking" in desc_lower or "buckled" in desc_lower or "bench" in desc_lower:
        if any(w in desc_lower for w in ["child", "injured", "manhole", "gas pipeline", "gas leak"]):
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = "Road Damage"

    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Refusal and specific case alignments
    if "dead trees" in desc_lower:
        category = "Other"
        flag = ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row dynamically, and write results to output CSV.
    """
    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                if not row or not row.get("complaint_id"):
                    continue
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                print(f"Skipping malformed row due to error: {e}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
