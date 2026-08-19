"""
UC-0A — Complaint Classifier
RICE → agents.md → skills.md → CRAFT workflow implementation.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "hospitalised", "hospitalized",
    "ambulance", "fire", "hazard", "fell", "collapse", "collapsed"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row into category, priority, reason, and flag.
    Enforces RICE rules from agents.md and skills.md.
    """
    cid = row.get("complaint_id", "")
    desc = row.get("description", "").strip()
    loc = row.get("location", "").strip()
    desc_lower = desc.lower()

    # Priority determination via severity keywords
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw), desc_lower):
            priority = "Urgent"
            break
            
    category = "Other"
    flag = ""
    reason = f"Classified based on complaint description: '{desc}'"

    # Rule-based matching with fallback & ambiguity check
    if "heritage" in desc_lower or "heritage" in loc.lower():
        category = "Heritage Damage"
        reason = f"Cites heritage zone impact: '{desc}'"
    elif "pothole" in desc_lower or "potholes" in desc_lower:
        category = "Pothole"
        reason = f"Cites pothole issue: '{desc}'"
    elif "collapse" in desc_lower or "crater" in desc_lower or "road damage" in desc_lower:
        category = "Road Damage"
        reason = f"Cites road structural damage: '{desc}'"
    elif "underpass flood" in desc_lower or "flooded" in desc_lower or "floods" in desc_lower:
        category = "Flooding"
        reason = f"Cites flooding conditions: '{desc}'"
    elif "drain" in desc_lower or "stormwater" in desc_lower:
        category = "Drain Blockage"
        reason = f"Cites drain blockage or drainage issue: '{desc}'"
    elif "garbage" in desc_lower or "waste" in desc_lower or "debris" in desc_lower:
        category = "Waste"
        reason = f"Cites waste accumulation: '{desc}'"
    elif "drilling" in desc_lower or "noise" in desc_lower or "idling" in desc_lower:
        category = "Noise"
        reason = f"Cites noise/disturbance: '{desc}'"
    elif "streetlight" in desc_lower or "light" in desc_lower:
        category = "Streetlight"
        reason = f"Cites streetlight failure: '{desc}'"
    elif "heat" in desc_lower or "sun" in desc_lower:
        category = "Heat Hazard"
        reason = f"Cites heat hazard: '{desc}'"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Genuinely ambiguous description requiring manual review: '{desc}'"

    # Ambiguity check for overlapping multi-issue descriptions
    if "channel rainwater" in desc_lower or "fields that channel" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous cause between flooding and road drainage: '{desc}'"

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results CSV.
    """
    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
