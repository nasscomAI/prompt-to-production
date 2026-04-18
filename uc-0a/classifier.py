"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re

# Classification Schema Constants
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single citizen complaint row.
    Enforces rules from agents.md:
    - category: Exactly one allowed string.
    - priority: Urgent if keywords present, else Standard or Low.
    - reason: Single sentence quoting text.
    - flag: NEEDS_REVIEW if ambiguous.
    """
    description = row.get("description", "").strip()
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }

    # Keyword-based heuristics for initial classification
    # Note: In a real agentic workflow, this would be a prompt to an LLM.
    # Here we implement the logic required by the RICE rules.
    
    desc_lower = description.lower()
    
    # 1. Category Inference
    category = "Other"
    flag = ""
    
    if any(k in desc_lower for k in ["pothole"]):
        category = "Pothole"
    elif any(k in desc_lower for k in ["flood", "waterlogged", "water standing"]):
        category = "Flooding"
    elif any(k in desc_lower for k in ["streetlight", "light out", "flickering"]):
        category = "Streetlight"
    elif any(k in desc_lower for k in ["garbage", "waste", "trash", "overflowing bin", "smell"]):
        category = "Waste"
    elif any(k in desc_lower for k in ["noise", "music", "loud"]):
        category = "Noise"
    elif any(k in desc_lower for k in ["drain", "sewage", "blocked"]):
        category = "Drain Blockage"
    elif any(k in desc_lower for k in ["cracked", "sinking", "road surface", "footpath"]):
        category = "Road Damage"
    elif any(k in desc_lower for k in ["heritage", "old city"]):
        category = "Heritage Damage"
    elif any(k in desc_lower for k in ["heat", "hot", "sun"]):
        category = "Heat Hazard"

    # Ambiguity check
    if category == "Other" or (category == "Flooding" and "drain" in desc_lower):
        flag = "NEEDS_REVIEW"

    # 2. Priority Inference
    priority = "Standard"
    if any(k in desc_lower for k in URGENT_KEYWORDS):
        priority = "Urgent"
    elif int(row.get("days_open", 0)) > 14:
        priority = "Standard" # High days open might be standard but urgent takes priority
    else:
        priority = "Standard" # Defaulting to standard per rules unless urgent
    
    # If no urgent keywords but high risk, could be low if minor. 
    # Let's stick to Standard/Urgent for most.
    if "smell" in desc_lower and priority != "Urgent":
        priority = "Low"

    # 3. Reason Generation (Cite specific words)
    # Finding the first matching keyword for the reason
    cited_words = []
    all_keywords = ["pothole", "flood", "streetlight", "garbage", "noise", "drain", "cracked", "heritage", "injury", "child", "hazard"]
    for k in all_keywords:
        if k in desc_lower:
            cited_words.append(k)
    
    if not cited_words:
        cited_words = description.split()[:3]
        
    joined_words = ", ".join(cited_words[:2])
    reason = "Classified as {} because description mentions '{}'.".format(category, joined_words)

    return {
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
        print("Error: Input file {} not found.".format(input_path))
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            for row in reader:
                classification = classify_complaint(row)
                # Merge original row with classification
                row.update(classification)
                results.append(row)

        if not results:
            print("No data found in input file.")
            return

        # Define output fieldnames (original + new fields)
        output_fields = fieldnames + ["category", "priority", "reason", "flag"]
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print("An error occurred during batch processing: {}".format(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to {}".format(args.output))
