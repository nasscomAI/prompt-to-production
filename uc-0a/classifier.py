"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Configuration from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "rain", "water", "inaccessible"],
    "Streetlight": ["streetlight", "light", "dark"],
    "Waste": ["garbage", "bins", "dumped", "waste", "smell", "animal"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["cracked", "sinking", "surface", "footpath", "tiles"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "hot"],
    "Drain Blockage": ["drain", "manhole", "sewage"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Determine Priority
    priority = "Standard"
    matched_urgent = [kw for kw in URGENT_KEYWORDS if kw in description]
    if matched_urgent:
        priority = "Urgent"
    
    # 2. Determine Category
    category = "Other"
    reason_keyword = ""
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                category = cat
                reason_keyword = kw
                break
        if category != "Other":
            break
            
    # 3. Determine Flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # 4. Construct Reason
    if matched_urgent and priority == "Urgent":
        reason = f"Priority is Urgent because the description mentions safety-critical words like '{matched_urgent[0]}'."
    elif reason_keyword:
        reason = f"Classified as {category} because the description mentions '{reason_keyword}'."
    else:
        reason = "Category is set to Other as no specific keywords were matched in the description."

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
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("description"):
                    # Handle missing descriptions as per skills.md error handling
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id')}: {e}")
                    # Continue processing other rows
    except Exception as e:
        print(f"Failed to read input CSV: {e}")
        return

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

