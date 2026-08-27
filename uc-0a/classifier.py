"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', '')
    
    category = "Other"
    priority = "Standard"
    reason = "No specific reason extracted."
    flag = ""
    
    # 1. Determine priority
    urgent_matches = [kw for kw in URGENT_KEYWORDS if kw in desc]
    if urgent_matches:
        priority = "Urgent"
        reason = f"Contains severity keyword(s): {', '.join(urgent_matches)}"
    
    # 2. Determine category
    # Priority matching based on obvious keywords
    if "pothole" in desc:
        category = "Pothole"
        if not urgent_matches:
            reason = "Description mentions 'pothole'."
    elif "flood" in desc:
        category = "Flooding"
        if not urgent_matches:
            reason = "Description mentions 'flood'."
    elif " streetlight" in desc or "lights out" in desc:
        category = "Streetlight"
        if not urgent_matches:
            reason = "Description mentions 'streetlight' or 'lights out'."
    elif "waste" in desc or "garbage" in desc:
        category = "Waste"
        if not urgent_matches:
            reason = "Description mentions 'waste' or 'garbage'."
    elif "noise" in desc or "music" in desc:
        category = "Noise"
        if not urgent_matches:
            reason = "Description mentions 'noise' or 'music'."
    elif "road" in desc and ("crack" in desc or "sink" in desc or "damage" in desc):
        category = "Road Damage"
        if not urgent_matches:
            reason = "Description mentions road damage/cracks."
    elif "heritage" in desc:
        category = "Heritage Damage"
        if not urgent_matches:
            reason = "Description mentions 'heritage'."
    elif "heat" in desc:
        category = "Heat Hazard"
        if not urgent_matches:
            reason = "Description mentions 'heat'."
    elif "drain" in desc or "manhole" in desc:
        category = "Drain Blockage"
        if not urgent_matches:
            reason = "Description mentions 'drain' or 'manhole'."
    else:
        # Ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        if not urgent_matches:
            reason = "Could not definitively determine category from description."

    # Edge cases from the prompt logic
    if category == "Other" and not flag:
        flag = "NEEDS_REVIEW"

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
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classification = classify_complaint(row)
                results.append(classification)
            except Exception as e:
                # Fallback on crash
                results.append({
                    "complaint_id": row.get('complaint_id', 'UNKNOWN'),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error formatting row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
