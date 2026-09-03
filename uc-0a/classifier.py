"""
UC-0A — Complaint Classifier
Implementation adhering to RICE rules, agents.md, and skills.md requirements.
"""
import argparse
import csv
import re
from typing import Dict

# Exact allowed category list per README.md schema
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

# Exact severity keywords that MUST trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "schools",
    "hospital", "hospitalised", "hospitalized", "ambulance", "fire",
    "hazard", "hazardous", "fell", "collapse", "collapsed", "collapsing"
]


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing complaint description.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    category = "Other"
    reason_snippet = description[:60]

    # Rule-based category matching (ordered by specificity)
    if re.search(r"\b(pothole|potholes)\b", desc_lower):
        category = "Pothole"
        match = re.search(r"[^.]*?\bpotholes?\b[^.]*", description, re.IGNORECASE)
        reason_snippet = match.group(0).strip() if match else "pothole reported in description"
    elif any(w in desc_lower for w in ["flooded", "floods", "flooding", "waterlogging", "inundated", "standing in water", "waterlogged"]):
        category = "Flooding"
        match = re.search(r"[^.]*?\b(flooded|floods|flooding|water)\b[^.]*", description, re.IGNORECASE)
        reason_snippet = match.group(0).strip() if match else "flooding reported in area"
    elif "drain" in desc_lower and any(w in desc_lower for w in ["block", "blocked", "clogged", "debris", "sewer", "mosquito"]):
        category = "Drain Blockage"
        match = re.search(r"[^.]*?\bdrain\b[^.]*", description, re.IGNORECASE)
        reason_snippet = match.group(0).strip() if match else "drain blockage reported"
    elif any(w in desc_lower for w in ["heritage", "monument", "historic", "museum", "step well", "ancient"]):
        category = "Heritage Damage"
        match = re.search(r"[^.]*?\b(heritage|historic|museum|monument)\b[^.]*", description, re.IGNORECASE)
        reason_snippet = match.group(0).strip() if match else "heritage site damage reported"
    elif any(w in desc_lower for w in ["heat", "heatwave", "44°c", "45°c", "52°c", "temperature", "sun", "melting", "burns"]):
        category = "Heat Hazard"
        match = re.search(r"[^.]*?\b(heat|temperature|sun|melting|burns|44°C|45°C|52°C)\b[^.]*", description, re.IGNORECASE)
        reason_snippet = match.group(0).strip() if match else "extreme heat hazard reported"
    elif any(w in desc_lower for w in ["streetlight", "streetlights", "light out", "lights out", "dark", "unlit", "substation", "flickering", "lamp post", "wiring theft"]):
        category = "Streetlight"
        match = re.search(r"[^.]*?\b(light|dark|unlit|lamp|substation|wiring)\b[^.]*", description, re.IGNORECASE)
        reason_snippet = match.group(0).strip() if match else "lighting issue reported"
    elif any(w in desc_lower for w in ["garbage", "waste", "trash", "dumped", "bins", "dead animal", "rubbish"]):
        category = "Waste"
        match = re.search(r"[^.]*?\b(garbage|waste|trash|dumped|animal|bins)\b[^.]*", description, re.IGNORECASE)
        reason_snippet = match.group(0).strip() if match else "waste disposal issue reported"
    elif any(w in desc_lower for w in ["music", "loudspeaker", "noise", "sound", "drilling", "amplifiers", "2am", "midnight"]):
        category = "Noise"
        match = re.search(r"[^.]*?\b(music|loudspeaker|noise|sound|drilling|amplifiers)\b[^.]*", description, re.IGNORECASE)
        reason_snippet = match.group(0).strip() if match else "noise nuisance reported"
    elif any(w in desc_lower for w in ["road", "footpath", "cracked", "sinking", "tiles", "manhole", "crater", "subsidence", "subsided", "cobblestones", "tarmac", "bridge"]):
        category = "Road Damage"
        match = re.search(r"[^.]*?\b(road|footpath|cracked|sinking|tiles|manhole|crater|subsidence)\b[^.]*", description, re.IGNORECASE)
        reason_snippet = match.group(0).strip() if match else "road or footpath damage reported"

    # Priority Evaluation
    found_keywords = [kw for kw in SEVERITY_KEYWORDS if re.search(r"\b" + kw, desc_lower)]
    if found_keywords:
        priority = "Urgent"
        kw_str = ", ".join(found_keywords)
        reason = f"Urgent priority due to safety trigger keyword(s) '{kw_str}' in description: '{reason_snippet}'."
    else:
        try:
            days = int(row.get("days_open", 0))
        except (ValueError, TypeError):
            days = 0

        if days >= 14:
            priority = "Urgent"
            reason = f"Urgent priority due to prolonged duration ({days} days open): '{reason_snippet}'."
        elif days >= 7:
            priority = "Standard"
            reason = f"Standard priority for category {category}: '{reason_snippet}'."
        else:
            priority = "Low" if days < 3 else "Standard"
            reason = f"Categorized as {category} based on description text: '{reason_snippet}'."

    # Flag Evaluation
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            # Combine classification with input row metadata for complete output
            output_row = {
                "complaint_id": classified["complaint_id"],
                "category": classified["category"],
                "priority": classified["priority"],
                "reason": classified["reason"],
                "flag": classified["flag"],
                "city": row.get("city", ""),
                "ward": row.get("ward", ""),
                "location": row.get("location", ""),
                "description": row.get("description", "")
            }
            results.append(output_row)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag", "city", "ward", "location", "description"]
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

