"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import os

# Taxonomy Rules from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity Rules from agents.md
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    desc_lower = description.lower()
    complaint_id = row.get("complaint_id", "Unknown")

    # 1. Category Classification (Strict Taxonomy Enforcement)
    category = "Other"
    
    if any(k in desc_lower for k in ["pothole", "crater"]):
        category = "Pothole"
    elif any(k in desc_lower for k in ["flood", "waterlog", "water accumulation"]):
        category = "Flooding"
    elif any(k in desc_lower for k in ["streetlight", "street light", "lamp", "dark road"]):
        category = "Streetlight"
    elif any(k in desc_lower for k in ["waste", "garbage", "trash", "dumping", "litter", "dead animal"]):
        category = "Waste"
    elif any(k in desc_lower for k in ["noise", "loud", "music"]):
        category = "Noise"
    elif any(k in desc_lower for k in ["drain", "sewage", "gutter", "drainage"]):
        category = "Drain Blockage"
    elif any(k in desc_lower for k in ["heritage", "monument", "historic"]):
        category = "Heritage Damage"
    elif any(k in desc_lower for k in ["heat", "sun", "hot"]):
        category = "Heat Hazard"
    elif any(k in desc_lower for k in ["road surface", "cracked", "pavement"]):
        category = "Road Damage"

    # 2. Priority Classification (Severity Enforcement)
    priority = "Standard"
    urgent_found = [k for k in URGENT_KEYWORDS if k in desc_lower]
    if urgent_found:
        priority = "Urgent"
    elif not description:
        priority = "Low"

    # 3. Reason Generation (One sentence, citing specific words)
    if not description:
        reason = "No description was provided for classification."
    elif urgent_found:
        reason = f"Priority is Urgent because the description mentions safety-critical words like '{urgent_found[0]}'."
    else:
        # Simple citation of category-related keyword
        reason = f"Classified as {category} based on the mention of issue-specific details in the description."

    # 4. Flag (NEEDS_REVIEW or blank)
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
            # Handle potential BOM or weird characters if necessary
            reader = csv.DictReader(f)
            for row in reader:
                if not any(row.values()): # Skip empty rows
                    continue
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Skipping row {row.get('complaint_id', 'unknown')} due to error: {e}")

        if not results:
            print("No valid rows found in input CSV.")
            return

        # Ensure output directory exists (if output_path contains a slash)
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Failed to process CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
