"""
UC-0A — Complaint Classifier
Implemented using RICE framework for consistent and verifiable urban governance.
"""
import argparse
import csv
import os

# --- ENFORCEMENT RULES (from agents.md) ---
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "sinkhole"],
    "Flooding": ["flood", "waterlogging", "submerged", "overflow"],
    "Streetlight": ["streetlight", "lamp", "dark", "light bulb"],
    "Waste": ["garbage", "trash", "waste", "rubbish", "dump"],
    "Noise": ["noise", "loud", "sound", "music"],
    "Road Damage": ["crack", "road broken", "pavement", "asphalt"],
    "Heritage Damage": ["heritage", "monument", "statue", "temple"],
    "Heat Hazard": ["heat", "hot", "temperature", "overheating"],
    "Drain Blockage": ["drain", "sewage", "clogged", "gutter", "blockage"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on instructions in agents.md.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Determine Category
    assigned_category = "Other"
    found_keywords = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                assigned_category = category
                found_keywords.append(kw)
                break
        if assigned_category != "Other":
            break

    # 2. Determine Priority
    priority = "Standard"
    urgent_found = [kw for kw in URGENT_KEYWORDS if kw in description]
    if urgent_found:
        priority = "Urgent"
    elif "low" in description or "minor" in description:
        priority = "Low"

    # 3. Generate Reason (Must cite specific words)
    if assigned_category != "Other":
        reason = f"Classified as {assigned_category} because description mentions '{found_keywords[0]}'."
    else:
        reason = "No specific category keywords found in description."

    if priority == "Urgent":
        reason += f" Priority set to Urgent due to keyword: '{urgent_found[0]}'."

    # 4. Handle Ambiguity (Rule: set flag if ambiguous)
    flag = ""
    if assigned_category == "Other" or not description:
        assigned_category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": assigned_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write back to output CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # Ensure we handle empty or malformed rows gracefully
                if not row:
                    continue
                classified = classify_complaint(row)
                results.append(classified)
                
        if not results:
            print("Warning: No records found to process.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"An error occurred during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input test CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
