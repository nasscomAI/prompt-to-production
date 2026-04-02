"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", 
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row deterministically based on RICE enforcement rules."""
    desc = row.get("description", "").lower()
    
    category = "Other"
    flag = ""
    reason = "No specific match found."
    
    if "pothole" in desc:
        category = "Pothole"
        reason = "Description contains 'pothole'."
    elif "drain" in desc and "block" in desc:
        category = "Drain Blockage"
        reason = "Description contains 'drain' and 'block'."
    elif "flood" in desc:
        category = "Flooding"
        reason = "Description contains 'flood'."
    elif "garbage" in desc or ("waste" in desc and "heritage" not in desc):
        category = "Waste"
        reason = "Description mentions garbage/waste."
    elif "drilling" in desc or "engines" in desc:
        category = "Noise"
        reason = "Description mentions drilling or engines."
    elif "heritage" in desc:
        category = "Heritage Damage"
        reason = "Description mentions heritage."
    elif "road collapsed" in desc or "crater" in desc:
        category = "Road Damage"
        reason = "Description mentions crater or road collapsed."
    elif "drain" in desc:
         category = "Drain Blockage"
         reason = "Description mentions drain."
    elif "rainwater through main road" in desc:
        category = "Flooding"
        reason = "Description implies flooding via rainwater."
    else:
        flag = "NEEDS_REVIEW"
        reason = "Ambiguous description, flagging for review."
        
    priority = "Standard"
    for word in URGENT_KEYWORDS:
        if word in desc:
            priority = "Urgent"
            reason += f" Priority escalated to Urgent because of keyword '{word}'."
            break
            
    row["category"] = category
    row["priority"] = priority
    row["reason"] = reason
    row["flag"] = flag
    return row


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        
        results = []
        for row in rows:
            try:
                results.append(classify_complaint(row))
            except Exception as e:
                print(f"Skipping row due to error: {e}")
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
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
