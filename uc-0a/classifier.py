"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Check severity keywords for Priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Urgent" if any(kw in desc for kw in severity_keywords) else "Standard"

    # Match Category
    category = "Other"
    
    # Heuristic mapping for categories
    if any(k in desc for k in ["pothole", "hole"]):
        category = "Pothole"
    elif any(k in desc for k in ["flood", "water"]):
        category = "Flooding"
    elif any(k in desc for k in ["light", "dark", "sparking"]):
        category = "Streetlight"
    elif any(k in desc for k in ["garbage", "waste", "smell", "dumped"]):
        category = "Waste"
    elif any(k in desc for k in ["noise", "music", "loud"]):
        category = "Noise"
    elif any(k in desc for k in ["road", "surface", "crack", "tiles", "broken"]):
        # Disambiguate with Pothole if pothole is present
        category = "Road Damage"
    elif any(k in desc for k in ["heritage", "monument"]):
        category = "Heritage Damage"
    elif any(k in desc for k in ["heat", "hot", "sun"]):
        category = "Heat Hazard"
    elif any(k in desc for k in ["drain", "blockage"]):
        category = "Drain Blockage"
        
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # Reason field extraction (first sentence containing keywords or just first sentence)
    reason = row.get("description", "").split(". ")[0].strip() + "." if ". " in row.get("description", "") else row.get("description", "")
    
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
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
            
            rows_to_write = []
            for row in reader:
                classification = classify_complaint(row)
                row.update(classification)
                rows_to_write.append(row)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
    except Exception as e:
        print(f"Error processing files: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
