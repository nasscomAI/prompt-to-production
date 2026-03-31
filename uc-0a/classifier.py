"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Taxonomy Enforcement
    categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"]
    category = "Other"
    flag = ""
    
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description or "water" in description:
        category = "Flooding"
    elif "light" in description or "dark" in description:
        category = "Streetlight"
    elif "garbage" in description or "waste" in description or "trash" in description or "bins" in description:
        category = "Waste"
    elif "noise" in description or "music" in description:
        category = "Noise"
    elif "crack" in description or "sinking" in description or "tiles" in description:
        category = "Road Damage"
    elif "heritage" in description:
        category = "Heritage Damage"
    elif "heat" in description or "sun" in description:
        category = "Heat Hazard"
    elif "drain" in description:
        category = "Drain Blockage"
    else:
        flag = "NEEDS_REVIEW"

    # 2. Severity Keywords for Urgent Priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for word in severity_keywords:
        if word in description:
            priority = "Urgent"
            break
    
    if "low" in description:
        priority = "Low"

    # 3. Reason (citing specific words)
    reason = f"Classified as {category} due to description content: '{description[:50]}...'"
    if priority == "Urgent":
        # Find which keyword triggered it for the reason
        triggered = [w for w in severity_keywords if w in description]
        reason += f" Priority set to Urgent due to keywords: {', '.join(triggered)}."

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
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id')}: {e}")

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
