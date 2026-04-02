"""
UC-0A — Complaint Classifier
Re-implementation following STBA Refined RICE framework.
"""
import argparse
import csv
import os

# Configuration from agents.md and README.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Heat Hazard": ["heat", "melting", "melted", "heatwave", "temperatures", "full sun"],
    "Heritage Damage": ["heritage", "historic", "ancient", "museum", "precinct"],
    "Pothole": ["pothole", "manhole"],
    "Flooding": ["flooded", "flooding", "floods", "waterlogging", "inundated", "rainwater"],
    "Streetlight": ["streetlight", "lights out", "unlit", "darkness", "lamp post"],
    "Waste": ["garbage", "trash", "waste", "dumped", "bins", "dead animal"],
    "Noise": ["music", "loud", "audible", "drilling", "amplifiers"],
    "Drain Blockage": ["drain", "sewage", "stormwater"],
    "Road Damage": ["surface cracked", "sinking", "subsidence", "tiles broken", "buckled", "road surface", "tarmac", "paving"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based enforcement.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Determine Priority
    priority = "Standard"
    found_urgent_trigger = None
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            found_urgent_trigger = kw
            break
    
    # 2. Determine Category
    category = "Other"
    found_category_trigger = None
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                category = cat
                found_category_trigger = kw
                break
        if category != "Other":
            break
            
    # 3. Determine Flag
    flag = ""
    if category == "Other" or not description.strip():
        flag = "NEEDS_REVIEW"
        
    # 4. Construct Reason
    if found_urgent_trigger and category != "Other":
        reason = f"Classified as {category} with Urgent priority because description mentions '{found_urgent_trigger}'."
    elif category != "Other":
        reason = f"Identified as {category} based on keywords like '{found_category_trigger}'."
    else:
        reason = "Category ambiguous; requires manual review."

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
    Ensures the script doesn't crash on bad rows and flags nulls.
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
                    print(f"Skipping malformed row {row.get('complaint_id')}: {e}")

        if not results:
            print("No results to write.")
            return

        keys = results[0].keys()
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Batch processing failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
