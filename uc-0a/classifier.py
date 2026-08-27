"""
UC-0A — Complaint Classifier
Implemented using RICE (Role, Intent, Context, Enforcement) based rules.
"""
import argparse
import csv
import re
import os

# Allowed categories from README.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger URGENT priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on strictly enforced rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Category Classification (Rule-based heuristic for this implementation)
    category = "Other"
    found_keywords = []
    
    mapping = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "water": "Flooding",
        "light": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "noise": "Noise",
        "loud": "Noise",
        "road": "Road Damage",
        "asphalt": "Road Damage",
        "heritage": "Heritage Damage",
        "monument": "Heritage Damage",
        "heat": "Heat Hazard",
        "hot": "Heat Hazard",
        "drain": "Drain Blockage",
        "sewer": "Drain Blockage"
    }
    
    for kw, cat in mapping.items():
        if kw in description:
            category = cat
            found_keywords.append(kw)
            break # Simple first-match for now
            
    # 2. Priority Enforcement
    priority = "Standard"
    trigger_word = None
    for word in SEVERITY_KEYWORDS:
        if word in description:
            priority = "Urgent"
            trigger_word = word
            break
            
    # 3. Reason Generation (Must cite specific words)
    if trigger_word and category != "Other":
        reason = f"Classified as {category} with Urgent priority due to the mention of '{trigger_word}'."
    elif category != "Other":
        reason = f"Classified as {category} based on keywords found in the description."
    else:
        reason = "Classified as Other because the description does not match specific category keywords."

    # 4. Ambiguity / Refusal Handling
    flag = ""
    if category == "Other" or not description:
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
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Failed to process row {row.get('complaint_id')}: {e}")

        if not results:
            print("No results to write.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
