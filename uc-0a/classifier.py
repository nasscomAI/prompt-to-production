"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint row based on instructions.
    """
    desc_lower = description.lower()
    
    # Categories and keywords
    categories = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging", "inundation"],
        "Streetlight": ["streetlight", "light", "lamp"],
        "Waste": ["waste", "garbage", "bin", "trash", "dump", "smell"],
        "Noise": ["noise", "loud", "music", "weeknight"],
        "Road Damage": ["cracked", "sinking", "road surface"],
        "Heritage Damage": ["heritage", "old city"],
        "Heat Hazard": ["heat", "sun", "hot"],
        "Drain Blockage": ["drain", "sewage", "overflow"],
    }
    
    category = "Other"
    for cat, keywords in categories.items():
        if any(kw in desc_lower for kw in keywords):
            category = cat
            break
            
    # Priority rules
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Urgent" if any(kw in desc_lower for kw in urgent_keywords) else "Standard"
    
    # Needs review flag
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    # Reason (simple citation)
    reason = "Cited keywords detected in description."
    if priority == "Urgent":
        triggered = [kw for kw in urgent_keywords if kw in desc_lower]
        reason = f"Urgent priority assigned due to mentions of: {', '.join(triggered)}."
    elif category != "Other":
        triggered = [kw for kw in categories[category] if kw in desc_lower]
        reason = f"Classified as {category} based on text: '{triggered[0]}'."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        
        for row in reader:
            classification = classify_complaint(row["description"])
            row.update(classification)
            results.append(row)

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
