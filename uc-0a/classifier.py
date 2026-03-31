"""
UC-0A — Complaint Classifier
Implementation based on RICE framework and schema enforcement.
"""
import argparse
import csv
import os

# Municipal Classification Schema Constraints
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based schema enforcement.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    # 1. Determine Priority (Severity Keyword check)
    priority = "Standard"
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = "Urgent"
            break
    
    # 2. Determine Category (Simplified keyword matching with fallback)
    category = "Other"
    flag = ""
    
    if "pothole" in description or "hole" in description:
        category = "Pothole"
    elif "flood" in description or "water" in description and "road" not in description:
        category = "Flooding"
    elif "light" in description or "dark" in description:
        category = "Streetlight"
    elif "waste" in description or "garbage" in description or "trash" in description:
        category = "Waste"
    elif "noise" in description or "loud" in description:
        category = "Noise"
    elif "road" in description or "crack" in description:
        category = "Road Damage"
    elif "heritage" in description or "statue" in description:
        category = "Heritage Damage"
    elif "heat" in description or "hot" in description:
        category = "Heat Hazard"
    elif "drain" in description or "sewer" in description:
        category = "Drain Blockage"
    
    # Ambiguity check
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # 3. Create Reason (One sentence citing words)
    reason = f"Classified based on description content."
    if priority == "Urgent":
        # Find exact keyword for the reason
        matched = [k for k in SEVERITY_KEYWORDS if k in description]
        reason = f"Urgent priority set due to the presence of severity keyword(s): {', '.join(matched)}."
    elif category != "Other":
        reason = f"Mapped to {category} due to description mentioning relevant environmental issues."
    
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
                classified = classify_complaint(row)
                results.append(classified)
        
        if not results:
            print("No data found in input CSV.")
            return

        # Write output
        keys = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Workflow failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
