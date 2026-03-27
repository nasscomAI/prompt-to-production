"""
UC-0A — Complaint Classifier
Implementation of the RICE rules defined in agents.md and skills.md.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", 
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def map_description_to_category(desc: str) -> str:
    desc_lower = desc.lower()
    if 'pothole' in desc_lower: return "Pothole"
    elif 'flood' in desc_lower or 'water log' in desc_lower: return "Flooding"
    elif 'light' in desc_lower or 'unlit' in desc_lower: return "Streetlight"
    elif 'waste' in desc_lower or 'garbage' in desc_lower or 'bin' in desc_lower: return "Waste"
    elif 'noise' in desc_lower or 'music' in desc_lower or 'loud' in desc_lower: return "Noise"
    elif 'road' in desc_lower and ('damage' in desc_lower or 'subsidence' in desc_lower) and 'heritage' not in desc_lower: return "Road Damage"
    elif 'heritage' in desc_lower: return "Heritage Damage"
    elif 'heat' in desc_lower or '44°c' in desc_lower or '45°c' in desc_lower or '52°c' in desc_lower or 'temperature' in desc_lower or 'sun' in desc_lower: return "Heat Hazard"
    elif 'drain' in desc_lower: return "Drain Blockage"
    return "Other"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '')
    desc_lower = desc.lower()
    
    # 1. Determine Category
    category = map_description_to_category(desc)
    
    # 2. Determine Priority
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break
            
    # 3. Determine Reason
    words = desc.split()
    cite_text = " ".join(words[:10])
    if len(words) > 10:
        cite_text += "..."
    reason = f"Based on '{cite_text}' in the description."
    
    # 4. Determine Flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get('complaint_id', ''),
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
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                out_row = dict(row)
                out_row['category'] = classified['category']
                out_row['priority'] = classified['priority']
                out_row['reason'] = classified['reason']
                out_row['flag'] = classified['flag']
                results.append(out_row)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                
    if not results:
        print("No results to write.")
        return
        
    fieldnames = list(results[0].keys())
    
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
