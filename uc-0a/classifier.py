"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md requirements.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based logic.
    Reflects RICE enforcement rules from agents.md.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Define Taxonomy and Keywords
    categories = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlog", "submerge", "underpass"],
        "Streetlight": ["streetlight", "street light", "dark", "lamp"],
        "Waste": ["garbage", "trash", "waste", "dump", "debris"],
        "Noise": ["noise", "loud", "sound", "volume"],
        "Road Damage": ["crack", "road damage", "pavement", "surface"],
        "Heritage Damage": ["heritage", "statue", "monument", "historic"],
        "Heat Hazard": ["heat", "hot", "sun", "shade", "water point"],
        "Drain Blockage": ["drain", "sewage", "blocked", "clogged", "gutter"],
    }
    
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # 2. Determine Category
    assigned_category = "Other"
    matching_keywords = []
    
    for category, keywords in categories.items():
        for kw in keywords:
            if kw in description:
                assigned_category = category
                matching_keywords.append(kw)
                break
        if assigned_category != "Other":
            break
            
    # 3. Determine Priority
    priority = "Standard"
    severity_trigger = None
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            severity_trigger = kw
            break
            
    # 4. Construct Reason
    if assigned_category != "Other":
        reason = f"Category assigned as {assigned_category} because description mentioned '{matching_keywords[0]}'."
    else:
        reason = "Category set to Other as no specific taxonomy keywords were detected in the description."
        
    if priority == "Urgent":
        reason += f" Priority elevated to Urgent due to safety keyword '{severity_trigger}'."
    
    # 5. Handle Ambiguity Flag
    # Set NEEDS_REVIEW if category is Other or if multiple categories might apply (simple implementation: if Other)
    flag = "NEEDS_REVIEW" if assigned_category == "Other" else ""
    
    return {
        "complaint_id": complaint_id,
        "category": assigned_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Ensures program doesn't crash on bad rows.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Clean the description for processing
                    if not row.get("description"):
                        row["description"] = ""
                    
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Warning: Failed to process row {row.get('complaint_id')}: {e}")
                    # Create a dummy failed row to maintain output count if possible
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Fatal Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
