"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on municipal rules.
    """
    description = row.get("description", "").lower()
    
    # Category detection
    categories = {
        "Pothole": ["pothole", "crater", "dip in road"],
        "Flooding": ["flood", "waterlogged", "water accumulation", "knee-deep"],
        "Streetlight": ["streetlight", "lamp", "darkness", "light not working"],
        "Waste": ["waste", "garbage", "trash", "dumping", "refuse"],
        "Noise": ["noise", "loudspeaker", "music", "construction sound"],
        "Road Damage": ["road damage", "asphalt", "cracks in road"],
        "Heritage Damage": ["heritage", "monument", "historic", "ancient"],
        "Heat Hazard": ["heat", "sunstroke", "cooling centre", "temperature"],
        "Drain Blockage": ["drain", "sewage", "gutter", "blockage"]
    }
    
    selected_category = "Other"
    found_term = ""
    for category, keywords in categories.items():
        for kw in keywords:
            if kw in description:
                selected_category = category
                found_term = kw
                break
        if selected_category != "Other":
            break
            
    # Priority detection
    priority_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_priority_term = ""
    
    for pk in priority_keywords:
        if pk in description:
            priority = "Urgent"
            found_priority_term = pk
            break
            
    # Reason and Flag
    flag = ""
    if selected_category == "Other":
        flag = "NEEDS_REVIEW"
        reasonArr = ["Category could not be determined from the description alone."]
    else:
        reasonArr = [f"Identified as {selected_category} due to '{found_term}'."]
    
    if priority == "Urgent":
        reasonArr.append(f"Marked Urgent because of risk associated with '{found_priority_term}'.")
    
    return {
        "complaint_id": row.get("complaint_id"),
        "category": selected_category,
        "priority": priority,
        "reason": " ".join(reasonArr),
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not any(row.values()): # skip empty rows
                    continue
                results.append(classify_complaint(row))
                
        if not results:
            print("No rows found in input.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error during batch classification: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
