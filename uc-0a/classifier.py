"""
UC-0A — Complaint Classifier
Implementation based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import os

# Configuration from agents.md
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
    Classifies a single complaint based on the description text.
    Returns: dict with keys matching the schema in skills.md
    """
    desc = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    category = "Other"
    priority = "Standard"
    reason = "No specific category matched from taxonomy."
    flag = ""

    # 1. Determine Category (Priority to specific keywords)
    if "pothole" in desc:
        category = "Pothole"
        reason = "Description mentions 'pothole'."
    elif "flood" in desc or "water" in desc and "drain" not in desc:
        category = "Flooding"
        reason = "Description mentions flooding or standing water."
    elif "drain" in desc or "manhole" in desc:
        category = "Drain Blockage"
        reason = "Description mentions blocked drains or manholes."
    elif "streetlight" in desc or "lights out" in desc:
        category = "Streetlight"
        reason = "Description refers to streetlight or lighting issues."
    elif "garbage" in desc or "waste" in desc or "dead animal" in desc:
        category = "Waste"
        reason = "Description refers to waste management or garbage."
    elif "music" in desc or "noise" in desc:
        category = "Noise"
        reason = "Description mentions noise or loud music."
    elif "heritage" in desc:
        category = "Heritage Damage"
        reason = "Description refers to a heritage site or structure."
    elif "heat" in desc or "temperature" in desc:
        category = "Heat Hazard"
        reason = "Description refers to extreme heat or temperature hazards."
    elif "road" in desc or "footpath" in desc or "surface" in desc:
        category = "Road Damage"
        reason = "Description refers to road or footpath damage."

    # 2. Determine Priority (Based on severity keywords)
    triggered_keywords = [word for word in SEVERITY_KEYWORDS if word in desc]
    if triggered_keywords:
        priority = "Urgent"
        reason += f" Priority set to Urgent due to safety keywords: {', '.join(triggered_keywords)}."
    elif "priority" in row and row["priority"]:
        priority = row["priority"]

    # 3. Handle Ambiguity
    if category == "Other" or not desc:
        flag = "NEEDS_REVIEW"
        if not desc:
            reason = "Description is empty."
        else:
            reason = "Ambiguous description - could not map to specific taxonomy."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, processes each row, and writes results to output CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                classified = classify_complaint(row)
                results.append(classified)
        
        if not results:
            print("No data found in input file.")
            return

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
