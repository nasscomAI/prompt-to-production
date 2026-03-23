"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    text = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # Severity keywords that must trigger Urgent
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    # Check for priority
    priority = "Standard"
    found_urgent_word = None
    for kw in urgent_keywords:
        if kw in text:
            priority = "Urgent"
            found_urgent_word = kw
            break
            
    # Simple category mapping
    category = "Other"
    flag = ""
    
    if "pothole" in text or "crater" in text:
        category = "Pothole"
    elif "flood" in text or "waterlogging" in text:
        category = "Flooding"
    elif "light" in text or "lamp" in text:
        category = "Streetlight"
    elif "waste" in text or "garbage" in text or "trash" in text:
        category = "Waste"
    elif "noise" in text or "loud" in text:
        category = "Noise"
    elif "road" in text and "damage" in text:
        category = "Road Damage"
    elif "heritage" in text or "monument" in text:
        category = "Heritage Damage"
    elif "heat" in text:
        category = "Heat Hazard"
    elif "drain" in text or "clog" in text or "sewer" in text:
        category = "Drain Blockage"
    else:
        # Ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    reason = "No specific issue identified."
    if priority == "Urgent":
        reason = f"The description mentions '{found_urgent_word}' which escalates this to Urgent priority."
    elif category != "Other":
        reason = f"Classified as {category} based on keywords in the description."
        
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if not row:
                    continue
                try:
                    classified = classify_complaint(row)
                    
                    # Merge original with new columns
                    out_row = dict(row)
                    out_row.update(classified)
                    results.append(out_row)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                    
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        return

    if not results:
        print("No results to write. Output not created.")
        return

    fieldnames = list(results[0].keys())
    
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
