"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine priority based on severity keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_urgent_kw = None
    
    for kw in urgent_keywords:
        if kw in desc:
            priority = "Urgent"
            found_urgent_kw = kw
            break
            
    # 2. Determine category
    category = "Other"
    if "heritage" in desc:
        category = "Heritage Damage"
    elif "pothole" in desc:
        category = "Pothole"
    elif "drain" in desc or "manhole" in desc:
        category = "Drain Blockage"
    elif "flood" in desc:
        category = "Flooding"
    elif "streetlight" in desc or "lights out" in desc:
        category = "Streetlight"
    elif "garbage" in desc or "waste" in desc:
        category = "Waste"
    elif "music" in desc or "noise" in desc:
        category = "Noise"
    elif "road" in desc or "footpath" in desc:
        category = "Road Damage"
        
    # Ensure exact allowed strings
    allowed_categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]
    if category not in allowed_categories:
        category = "Other"
        
    # 3. Flag ambiguous items ("Other" category)
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    # 4. Reason generation explicitly citing specific words
    if priority == "Urgent":
        reason = f"Priority is Urgent because the description contains the severity keyword '{found_urgent_kw}'."
    else:
        reason = f"Assigned to {category} based on description keywords."
    
    if flag == "NEEDS_REVIEW":
        reason += " Requires review due to ambiguous category."
        
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must handle missing/bad rows gracefully.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        sys.exit(1)
        
    results = []
    
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            print("Error: Empty or invalid input CSV.")
            sys.exit(1)
            
        for idx, row in enumerate(reader):
            try:
                if not row.get("complaint_id"):
                    continue # Skip empty rows
                
                classification = classify_complaint(row)
                results.append(classification)
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                # Continue processing even if some rows fail
                
    if not results:
        print("No valid rows parsed.")
        sys.exit(1)
        
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
