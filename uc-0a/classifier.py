"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    category = "Other"
    reason_words = []
    
    if "pothole" in desc:
        category = "Pothole"
        reason_words.append("pothole")
    elif "flood" in desc or ("rain" in desc and "underpass" in desc):
        category = "Flooding"
        reason_words.append("flood")
    elif "drain" in desc:
        category = "Drain Blockage"
        reason_words.append("drain")
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
        reason_words.append("light")
    elif "garbage" in desc or "waste" in desc or "animal" in desc:
        category = "Waste"
        reason_words.append("garbage" if "garbage" in desc else "waste" if "waste" in desc else "animal")
    elif "music" in desc or "noise" in desc:
        category = "Noise"
        reason_words.append("music" if "music" in desc else "noise")
    elif "road" in desc and ("crack" in desc or "util" in desc or "sink" in desc or "damage" in desc):
        category = "Road Damage"
        reason_words.append("road")
    elif "heritage" in desc:
        category = "Heritage Damage"
        reason_words.append("heritage")
    elif "footpath" in desc or "manhole" in desc:
        category = "Road Damage"
        reason_words.append("footpath" if "footpath" in desc else "manhole")
        
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            reason_words.append(kw)
            
    reason = f"Keywords found: {', '.join(set(reason_words))}" if reason_words else "Unclear or missing markers"
    if flag == "NEEDS_REVIEW":
        reason = "Category is ambiguous"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames if reader.fieldnames else []
        
    output_fields = [f for f in fieldnames if f not in ("category", "priority_flag")]
    output_fields.extend(["category", "priority", "reason", "flag"])
    
    results = []
    for row in rows:
        try:
            clf = classify_complaint(row)
            out_row = {k: v for k, v in row.items() if k in output_fields}
            out_row.update(clf)
            results.append(out_row)
        except Exception as e:
            print(f"Failed to process row: {e}")
            
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
