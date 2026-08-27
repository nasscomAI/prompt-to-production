"""
UC-0A — Complaint Classifier
Implemented based on agents.md and skills.md requirements.
"""
import argparse
import csv
import os

# Allowed values from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(description: str) -> dict:
    """
    Classifies a single complaint description into municipal categories and determines priority.
    """
    desc_lower = description.lower()
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    # Rule-based Category Determination
    if "pothole" in desc_lower:
        category = "Pothole"
        reason = f"Cites '{description.split('pothole')[0].split()[-1] if 'pothole' in desc_lower and len(description.split('pothole')[0].split()) > 0 else ''} pothole' found in description."
    elif "flood" in desc_lower or "water" in desc_lower:
        if "drain" in desc_lower or "sewer" in desc_lower or "blockage" in desc_lower:
            category = "Drain Blockage"
            reason = "Mentions of water and drain/blockage indicate a drain issue."
        else:
            category = "Flooding"
            reason = "Mentions of flooding or water accumulation."
    elif "light" in desc_lower or "dark" in desc_lower:
        if "heritage" in desc_lower:
            category = "Heritage Damage"
            reason = "Issue involving lights in a heritage area."
        else:
            category = "Streetlight"
            reason = "Complaint regarding streetlights or darkness."
    elif "garbage" in desc_lower or "waste" in desc_lower or "bin" in desc_lower or "dump" in desc_lower or "animal" in desc_lower:
        category = "Waste"
        reason = "Keywords like 'garbage', 'waste', or 'dumped' suggest a waste management issue."
    elif "noise" in desc_lower or "music" in desc_lower or "loud" in desc_lower:
        category = "Noise"
        reason = "Keywords related to noise or music detected."
    elif "road" in desc_lower or "crack" in desc_lower or "footpath" in desc_lower or "tiles" in desc_lower or "manhole" in desc_lower:
        category = "Road Damage"
        reason = "References to road surfaces, footpaths, or manhole covers."
    elif "heat" in desc_lower or "hot" in desc_lower:
        category = "Heat Hazard"
        reason = "Concerns regarding extreme heat or temperature."
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
        reason = "Direct mention of heritage structure or area."
    elif "drain" in desc_lower or "blockage" in desc_lower:
        category = "Drain Blockage"
        reason = "Issues with drains or blockages."

    # Specific Reason Refinement (citing words)
    if not reason:
        reason = "Generic classification based on keyword matching."
    else:
        # Try to find a specific word to cite
        words = desc_lower.split()
        for word in words:
            if word in desc_lower and word in ["pothole", "flooded", "streetlight", "garbage", "noise", "crack", "heritage", "drain"]:
                reason = f"Classified as {category} because description mentions '{word}'."
                break

    # Priority Enforcement
    triggered_keywords = [word for word in URGENT_KEYWORDS if word in desc_lower]
    if triggered_keywords:
        priority = "Urgent"
        reason += f" Priority set to Urgent due to: {', '.join(triggered_keywords)}."
    
    # Ambiguity check
    if category == "Other" or len(description.split()) < 4:
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, classifies each row, and writes results to output CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                print("Error: Empty CSV or missing header.")
                return
            
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            results = []
            for row in reader:
                desc = row.get("description", "")
                if not desc:
                    classification = {
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "N/A - Empty description.",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    classification = classify_complaint(desc)
                
                row.update(classification)
                results.append(row)

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
