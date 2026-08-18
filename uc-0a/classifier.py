"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import os

# Configuration from agents.md and README.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "sinkhole"],
    "Flooding": ["flood", "waterlogging", "inundated", "water-logged"],
    "Streetlight": ["streetlight", "street light", "lamp", "darkness", "lighting"],
    "Waste": ["garbage", "waste", "trash", "dump", "litter", "overflowing bin"],
    "Noise": ["noise", "loud", "music", "construction sound", "disturbance"],
    "Road Damage": ["cracks", "pavement", "sidewalk", "divider", "damaged road"],
    "Heritage Damage": ["heritage", "monument", "statue", "temple damage", "historic"],
    "Heat Hazard": ["heat", "sunstroke", "exhausted", "high temperature", "shade"],
    "Drain Blockage": ["drain", "sewage", "gutter", "clogged", "overflowing drain"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based logic.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Determine Category
    category = "Other"
    matched_words = []
    
    # Prioritize Drain Blockage if mentioned as it's often more specific than generic flooding
    search_order = ["Drain Blockage", "Flooding", "Pothole", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard"]
    
    found = False
    for cat in search_order:
        keywords = CATEGORY_KEYWORDS.get(cat, [])
        for kw in keywords:
            if kw in description:
                category = cat
                matched_words.append(kw)
                found = True
                break
        if found: break

    # 2. Determine Priority
    priority = "Standard"
    severity_trigger = None
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            severity_trigger = kw
            break
    
    if priority != "Urgent" and ("urgent" in description or "immediate" in description):
        priority = "Standard" # Default fallback unless severity keywords met

    # 3. Generate Reason
    if category != "Other" and matched_words:
        reason = f"Classified as {category} because description mentions '{matched_words[0]}'."
    else:
        reason = "Classified as Other due to lack of specific category keywords."
        
    if priority == "Urgent" and severity_trigger:
        reason += f" Priority set to Urgent due to keyword '{severity_trigger}'."

    # 4. Set Flag
    flag = ""
    # If category is Other or description is too short, mark for review
    if category == "Other" or len(description.split()) < 5:
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
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Warning: Skipping malformed row {row.get('complaint_id', 'unknown')}: {e}")
                    
        if not results:
            print("No data processed.")
            return

        keys = results[0].keys()
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Critical Error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
