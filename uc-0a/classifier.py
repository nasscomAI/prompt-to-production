"""
UC-0A — Complaint Classifier
RICE enforcement implementation for citizen complaint classification.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to RICE rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()
    
    # Priority keyword check
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"
    
    # Category determination
    flag = ""
    category = "Other"
    
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "drain blocked" in desc_lower or "manhole" in desc_lower:
        category = "Drain Blockage"
    elif "flooded" in desc_lower or "floods" in desc_lower:
        category = "Flooding"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"
    elif "lights out" in desc_lower or "streetlight" in desc_lower or "dark at night" in desc_lower:
        category = "Streetlight"
    elif "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower:
        category = "Waste"
    elif "music" in desc_lower or "noise" in desc_lower:
        category = "Noise"
    elif "cracked" in desc_lower or "footpath" in desc_lower or "road surface" in desc_lower:
        category = "Road Damage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Reason generation citing specific words from description
    matched_words = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if matched_words:
        reason = f"Classified as {priority} {category} because description mentions '{matched_words[0]}': \"{desc}\"."
    else:
        reason = f"Classified as {priority} {category} based on description text: \"{desc}\"."

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
    results = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
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

