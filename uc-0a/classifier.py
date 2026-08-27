"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based keyword mapping.
    Ensures zero taxonomy drift and strict adherence to safety priority logic.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Determine Category
    category_map = {
        "Pothole": ["pothole", "pit", "crater"],
        "Flooding": ["flood", "waterlog", "submerge", "inundat"],
        "Streetlight": ["streetlight", "street light", "lamp", "dark", "no light"],
        "Waste": ["waste", "garbage", "trash", "dump", "muck"],
        "Noise": ["noise", "loud", "sound", "music"],
        "Road Damage": ["road damage", "crack", "surface", "tarmac"],
        "Heritage Damage": ["heritage", "monument", "statue", "historical"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "burn"],
        "Drain Blockage": ["drain", "sewage", "overflow", "gutter"],
    }
    
    category = "Other"
    matched_cat_word = ""
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in description:
                category = cat
                matched_cat_word = kw
                break
        if category != "Other":
            break
            
    # 2. Determine Priority (Safety keywords)
    safety_keywords = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    
    priority = "Standard" # Default
    matched_safety_word = ""
    for kw in safety_keywords:
        if kw in description:
            priority = "Urgent"
            matched_safety_word = kw
            break
            
    # 3. Generate Reason
    if matched_cat_word and matched_safety_word:
        reason = f"Classified as {category} due to '{matched_cat_word}' and priority set to Urgent because of '{matched_safety_word}' in the description."
    elif matched_cat_word:
        reason = f"Identified as {category} based on the mention of '{matched_cat_word}' in the complaint."
    elif matched_safety_word:
        reason = f"Set to {priority} due to high-risk keyword '{matched_safety_word}' found in the text."
    else:
        reason = "Placed in Other category as the description does not contain specific keywords from the urban schema."

    # 4. Handle Ambiguity/Flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write output CSV with results.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # Handle null/missing description
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "MISSING"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description field.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                    
                # Classify the row
                classification = classify_complaint(row)
                results.append(classification)
                
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
