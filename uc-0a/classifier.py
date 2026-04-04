import argparse
import csv
import os
import sys

# Constants defined by the UC-0A Schema
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

URGENT_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(description):
    """
    Skill: classify_complaint
    Implements strict keyword checks and taxonomy mapping.
    """
    desc_lower = description.lower()
    
    # 1. Determine Priority (Enforcement Rule 2)
    priority = "Standard"
    triggered_keywords = [k for k in URGENT_KEYWORDS if k in desc_lower]
    if triggered_keywords:
        priority = "Urgent"
    
    # 2. Determine Category & Flag (Enforcement Rule 1 & 4)
    # Simple keyword-to-category mapping for implementation
    category = "Other"
    flag = ""
    
    mapping = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "light": "Streetlight",
        "garbage": "Waste",
        "noise": "Noise",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage"
    }
    
    found_categories = [val for key, val in mapping.items() if key in desc_lower]
    
    if len(found_categories) == 1:
        category = found_categories[0]
    elif len(found_categories) > 1 or not found_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 3. Generate Reason (Enforcement Rule 3)
    if priority == "Urgent":
        reason = f"Priority set to Urgent because description mentions {triggered_keywords[0]}."
    else:
        reason = f"Classified as {category} based on the mention of relevant infrastructure issues."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path, output_path):
    """
    Skill: batch_classify
    Handles file I/O and error states for the CSV processing.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Expecting 'description' column based on UC README
                desc = row.get('description', '')
                classification = classify_complaint(desc)
                
                # Merge original row data with new classification
                output_row = {**row, **classification}
                results.append(output_row)

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            if not results:
                return
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Error processing CSV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input test CSV")
    parser.add_argument("--output", required=True, help="Name of output CSV file")
    
    args = parser.parse_args()
    
    # Run command expects uc-0a/ prefix in output as per README
    final_output_path = os.path.join("uc-0a", args.output)
    
    try:
        batch_classify(args.input, final_output_path)
        print(f"Success: Results written to {final_output_path}")
    except FileNotFoundError as e:
        print(f"Skill Error (batch_classify): {e}")
        sys.exit(1)