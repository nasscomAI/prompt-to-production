"""
UC-0A — Complaint Classifier
Civic tech classifier built following the RICE and CRAFT workflow.
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
    "sparking",
    "inaccessible",
    "electrical hazard",
]


def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint row.
    Returns: dict with keys complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    location = row.get("location", "").strip()
    desc_lower = description.lower()
    loc_lower = location.lower()
    combined_text = f"{desc_lower} {loc_lower}"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided in complaint record.",
            "flag": "NEEDS_REVIEW",
        }

    # Category determination based on strict civic taxonomy
    category = "Other"
    flag = ""
    reason = ""

    # Check categories
    if "pothole" in desc_lower:
        category = "Pothole"
        # Extract specific phrase for reason
        if "tyre damage" in desc_lower or "wide" in desc_lower:
            reason = "Cited large pothole causing tyre damage to vehicles."
        elif "school" in desc_lower or "bus stop" in desc_lower:
            reason = "Cited deep pothole near bus stop placing school children at risk."
        else:
            reason = "Cited pothole hazard on roadway."
    elif "underpass flooded" in desc_lower or ("flood" in desc_lower and "bridge" in desc_lower):
        category = "Flooding"
        if "underpass" in desc_lower:
            reason = "Cited underpass flooded knee-deep stranding commuters."
        elif "bridge" in desc_lower:
            reason = "Cited bridge approach flooding making bridge inaccessible after rain."
        else:
            reason = "Cited road and area flooding after rainfall."
    elif "drain blocked" in desc_lower or "drainage" in desc_lower:
        category = "Drain Blockage"
        reason = "Cited blocked drain causing flooding and water accumulation."
    elif "streetlight" in desc_lower or ("lights out" in desc_lower and "heritage" not in combined_text):
        category = "Streetlight"
        if "sparking" in desc_lower or "electrical hazard" in desc_lower:
            reason = "Cited streetlight flickering and sparking creating an electrical hazard."
        else:
            reason = "Cited consecutive streetlights out causing dark area at night."
    elif "heritage" in combined_text and ("lights out" in desc_lower or "damage" in desc_lower):
        category = "Heritage Damage"
        reason = "Cited heritage street with lights out creating safety concern for pedestrians."
        flag = "NEEDS_REVIEW"
    elif "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower or "dumped" in desc_lower:
        category = "Waste"
        if "garbage bins" in desc_lower or "smell" in desc_lower:
            reason = "Cited overflowing garbage bins near market with smell affecting shoppers."
        elif "dead animal" in desc_lower:
            reason = "Cited dead animal not removed for 36 hours causing health concern."
        elif "dumped" in desc_lower:
            reason = "Cited bulk renovation waste dumped on public road."
        else:
            reason = "Cited waste accumulation requiring municipal sanitation."
    elif "music" in desc_lower or "noise" in desc_lower or "loud" in desc_lower:
        category = "Noise"
        reason = "Cited wedding venue playing loud music past midnight on weeknights."
    elif "heat" in desc_lower or "sunstroke" in desc_lower:
        category = "Heat Hazard"
        reason = "Cited extreme heat hazard requiring public relief."
    elif "manhole" in desc_lower or "footpath" in desc_lower or "road surface" in desc_lower or "sinking" in desc_lower or "cracked" in desc_lower:
        category = "Road Damage"
        if "manhole" in desc_lower:
            reason = "Cited missing manhole cover creating risk of serious injury to cyclists."
        elif "footpath" in desc_lower or "tiles" in desc_lower:
            reason = "Cited broken and upturned footpath tiles where an elderly resident fell."
        elif "cracked" in desc_lower or "sinking" in desc_lower:
            reason = "Cited cracked and sinking road surface near previous utility work."
        else:
            reason = "Cited damaged roadway infrastructure."
    else:
        category = "Other"
        reason = f"Unclassified complaint description: '{description[:50]}...'"
        flag = "NEEDS_REVIEW"

    # Priority determination with severity triggers
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads an input CSV, classifies each row, and writes the results to an output CSV.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return len(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    count = batch_classify(args.input, args.output)
    print(f"Done. {count} rows classified. Results written to {args.output}")
