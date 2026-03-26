"""
UC-0A — Complaint Classifier
Implementation based on RICE (agents.md) and skills (skills.md).
"""
import argparse
import csv
import os

# RICE ENFORCEMENT CONSTANTS
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single complaint row based on RICE enforcement rules.
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()
    
    # 1. Determine Category (following the taxonomy)
    category = "Other"
    flag = "NEEDS_REVIEW"
    
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "drain" in desc_lower or "manhole" in desc_lower:
        category = "Drain Blockage"
    elif "flood" in desc_lower or "rain" in desc_lower or "water" in desc_lower or "underpass" in desc_lower:

        category = "Flooding"
    elif "light" in desc_lower or "dark" in desc_lower or "sparking" in desc_lower:
        category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "dumped" in desc_lower or "animal" in desc_lower:
        category = "Waste"
    elif "noise" in desc_lower or "music" in desc_lower or "midnight" in desc_lower:
        category = "Noise"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
    elif "heat" in desc_lower or "hot" in desc_lower:
        category = "Heat Hazard"
    elif "road" in desc_lower or "cracked" in desc_lower or "surface" in desc_lower or "broken" in desc_lower or "sinking" in desc_lower:
        category = "Road Damage"


    # Reset flag if category was determined
    if category != "Other":
        flag = ""

    # 2. Determine Priority (Urgent triggers)
    priority = "Standard"
    triggered_words = [word for word in URGENT_KEYWORDS if word in desc_lower]
    if triggered_words:
        priority = "Urgent"

    # 3. Generate Reason (Must cite specific words)
    if category != "Other":
        cite_desc = desc[:60] + "..." if len(desc) > 60 else desc
        reason = f"Classified as {category} because description mentions '{cite_desc}'"
    else:
        reason = "Category ambiguous from description provided."

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, applies classify_complaint per row, writes output CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

        if not results:
            print("No results generated.")
            return

        keys = results[0].keys()
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Failed to process batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

