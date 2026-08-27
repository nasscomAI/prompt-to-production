"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on keywords for category and priority.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    description_lower = description.lower()
    
    # Priority Enforcement: Trigger 'Urgent' if safety keywords are present
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_priority_keywords = [kw for kw in urgent_keywords if kw in description_lower]
    priority = "Urgent" if found_priority_keywords else "Standard"
    
    # Category Enforcement: Taxonomy mapping
    categories = {
        "Pothole": ["pothole", "pit", "crater"],
        "Flooding": ["flood", "waterlog", "submerge", "inundate"],
        "Streetlight": ["streetlight", "lamp", "dark", "street light"],
        "Waste": ["waste", "garbage", "trash", "dump", "refuse", "litter", "dead animal"],
        "Noise": ["noise", "loud", "sound", "music", "construction"],
        "Road Damage": ["road surface", "pavement", "asphalt", "cracked", "sinking"],
        "Heritage Damage": ["heritage", "monument", "statue", "ancient", "historic"],
        "Heat Hazard": ["heat", "hot", "sun", "burn", "temperature"],
        "Drain Blockage": ["drain", "gutter", "sewage", "clog", "blocked", "manhole"],
    }
    
    category = "Other"
    reason: str = "No specific category keywords matched in the description."
    flag = ""
    
    for cat, keywords in categories.items():
        matched_keywords = [kw for kw in keywords if kw in description_lower]
        if matched_keywords:
            category = cat
            reason = f"Classified as {cat} because the description mentions '{matched_keywords[0]}'."
            break
            
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # Reason formatting: Ensure it's one sentence and cites priority reason if Urgent
    if priority == "Urgent":
        reason += f" Priority is Urgent due to safety-critical keyword: '{found_priority_keywords[0]}'."
        
    return {
        "complaint_id": row.get("complaint_id", "N/A"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write the result to a CSV file.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                print(f"Error processing complaint {row.get('complaint_id', 'Unknown')}: {e}")
                
    if not results:
        print("No complaints were successfully processed.")
        return
        
    # Ensure output directory exists if specified
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    
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
