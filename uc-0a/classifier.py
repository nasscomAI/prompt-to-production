"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()
    
    priority = "Standard"
    reason_words = []
    
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            reason_words.append(kw)
    
    if reason_words:
        reason = f"The description contains severity keywords: {', '.join(reason_words)}."
    else:
        priority = "Standard"
        reason = "No severity keywords were found in the description."

    category = "Other"
    flag = ""
    
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description or "water" in description:
        category = "Flooding"
    elif "light" in description or "dark" in description:
        category = "Streetlight"
    elif "waste" in description or "garbage" in description or "trash" in description:
        category = "Waste"
    elif "noise" in description or "loud" in description:
        category = "Noise"
    elif "road" in description and "damage" in description:
        category = "Road Damage"
    elif "heritage" in description:
        category = "Heritage Damage"
    elif "heat" in description:
        category = "Heat Hazard"
    elif "drain" in description:
        category = "Drain Blockage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    results = []
    fieldnames = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames)
            for col in ["category", "priority", "reason", "flag"]:
                if col not in fieldnames:
                    fieldnames.append(col)
                    
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                    results.append(row)
                except Exception as e:
                    print(f"Error classifying row: {e}")
                    row["flag"] = "ERROR"
                    results.append(row)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
        
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully processed {len(results)} rows and saved to {output_path}")
    except Exception as e:
        print(f"Error writing to output file {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
