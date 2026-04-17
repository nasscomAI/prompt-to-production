"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on keywords and description.
    """
    description = row.get("description", "").strip()
    desc_lower = description.lower()
    
    # 1. Category Mapping (Strict Allowed Values)
    category_map = {
        "Pothole": ["pothole", "crater", "hole", "cavity"],
        "Flooding": ["flood", "waterlog", "inundation", "submerged"],
        "Streetlight": ["streetlight", "lamp", "dark", "no light", "bulb"],
        "Waste": ["waste", "garbage", "trash", "litter", "dump", "refuse"],
        "Noise": ["noise", "loud", "sound", "speaker", "disturb", "music"],
        "Road Damage": ["road damage", "crack", "surface", "broken road", "asphalt"],
        "Heritage Damage": ["heritage", "monument", "statue", "ancient", "historical", "temple"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "temperature", "blistering"],
        "Drain Blockage": ["drain", "sewage", "overflow", "choke", "gutter", "culvert"]
    }
    
    category = "Other"
    evidence_word = ""
    
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                evidence_word = kw
                break
        if category != "Other":
            break
            
    # 2. Priority Logic
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    severity_match = ""
    
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            severity_match = kw
            break
    
    # 3. Reason Generation (One sentence citing words)
    if category != "Other":
        reason = f"Classified as {category} because the description mentions '{evidence_word}'."
    else:
        reason = "Classified as Other because no specific infrastructure keywords were detected."
        
    if priority == "Urgent":
        reason += f" Priority escalated to Urgent due to safety-related keyword '{severity_match}'."
    
    # 4. Flagging Ambiguity
    flag = ""
    if category == "Other" or not description:
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": row.get("complaint_id", "Unknown"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write to results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Skipping malformed row: {e}")
                    
        if not results:
            print("No data to classify.")
            return

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Fatal error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

