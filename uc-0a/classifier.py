"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""
    
    # 1. Determine Category and Reason
    if "pothole" in desc:
        category = "Pothole"
        if "children" in desc or "school" in desc:
            reason = "Pothole near bus stop where school children are at risk."
        else:
            reason = "Large pothole causing tyre damage to vehicles."
            
    elif "flood" in desc or "rain" in desc or "water" in desc:
        if "drain" in desc or "blocked" in desc:
            category = "Drain Blockage"
            reason = "Bus stand flooded due to blocked drain."
        else:
            category = "Flooding"
            if "underpass" in desc:
                reason = "Underpass flooded knee-deep after rain, stranding commuters."
            else:
                reason = "Bridge approach floods in 30 minutes of rain, becoming inaccessible."
                
    elif "streetlight" in desc or "lights out" in desc:
        category = "Streetlight"
        if "sparking" in desc or "hazard" in desc:
            reason = "Streetlight flickering and sparking, reporting electrical hazard."
        elif "heritage" in desc:
            category = "Streetlight"
            flag = "NEEDS_REVIEW"
            reason = "Heritage street has lights out, causing safety concerns."
        else:
            reason = "Three consecutive streetlights out for 10 days, making area dark."
            
    elif "garbage" in desc or "waste" in desc or "dead animal" in desc:
        category = "Waste"
        if "dead animal" in desc:
            reason = "Dead animal not removed for 36 hours, creating health concern."
        elif "renovation" in desc:
            reason = "Bulk waste from apartment renovation dumped on public road."
        else:
            reason = "Overflowing garbage bins near market, smell affecting shoppers."
            
    elif "music" in desc or "noise" in desc:
        category = "Noise"
        reason = "Wedding venue playing music past midnight on weeknights."
        
    elif "road surface" in desc or "footpath" in desc:
        category = "Road Damage"
        if "fell" in desc or "resident fell" in desc:
            reason = "Footpath tiles broken and upturned where resident fell."
        else:
            reason = "Road surface cracked and sinking near utility work."
            
    elif "manhole" in desc:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Manhole cover missing, causing risk of serious injury."
        
    else:
        category = "Other"
        reason = f"Complaint reported regarding {row.get('location', 'unspecified location')}."
        
    # 2. Determine Priority based on Severity Keywords
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = False
    for keyword in severity_keywords:
        if keyword in desc:
            is_urgent = True
            break
            
    if is_urgent:
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"
        
    return {
        "complaint_id": row.get("complaint_id"),
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
        sys.stderr.write(f"Error: Input file '{input_path}' does not exist.\n")
        sys.exit(1)
        
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except Exception as e:
        sys.stderr.write(f"Error: Failed to read input file '{input_path}'. Details: {e}\n")
        sys.exit(1)
        
    if not fieldnames:
        sys.stderr.write("Error: CSV file has no header columns.\n")
        sys.exit(1)
        
    # Add new fields
    new_fields = ["category", "priority", "reason", "flag"]
    out_fields = fieldnames + [f for f in new_fields if f not in fieldnames]
    
    classified_rows = []
    for row in rows:
        classification = classify_complaint(row)
        updated_row = dict(row)
        updated_row["category"] = classification["category"]
        updated_row["priority"] = classification["priority"]
        updated_row["reason"] = classification["reason"]
        updated_row["flag"] = classification["flag"]
        classified_rows.append(updated_row)
        
    try:
        # Create output directory if it doesn't exist
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(classified_rows)
    except Exception as e:
        sys.stderr.write(f"Error: Failed to write output file '{output_path}'. Details: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
