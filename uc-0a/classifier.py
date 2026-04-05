"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on Senior Hyderabad Auditor rules.
    """
    desc = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', 'Unknown')
    
    # Default values
    category = "Sanitation"
    priority = "Low"
    reason = "General maintenance request."
    flag = "None"

    # Enforcement Rule 1: Category Mapping
    if any(word in desc for word in ["water", "leak", "pipe", "drain"]):
        category = "Water Supply"
    elif any(word in desc for word in ["pothole", "road", "tarmac", "flyover"]):
        category = "Road Repair"
    elif any(word in desc for word in ["light", "dark", "electric", "pole"]):
        category = "Street Lighting"
    elif any(word in desc for word in ["encroach", "shop", "footpath", "illegal"]):
        category = "Encroachment"

    # Enforcement Rule 2 & 3: Critical/High Priority Triggers
    if any(word in desc for word in ["open manhole", "death", "injury", "hospital", "flooding"]):
        priority = "Critical"
        reason = "Safety hazard or critical infrastructure access at risk."
    elif any(word in desc for word in ["metro", "charminar", "hitec", "flyover"]):
        priority = "High"
        reason = "Located in high-traffic Hyderabad transit zone."

    # Enforcement Rule 4: Refusal/Invalid
    if len(desc.split()) < 3:
        category = "Invalid"
        reason = "Insufficient detail provided in description."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(classify_complaint(row))

    if results:
        keys = results[0].keys()
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully processed {len(results)} complaints into {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)