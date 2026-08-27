"""
UC-0A — Complaint Classifier
Implemented using the RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import os

# Allowed categories from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority (from agents.md)
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules in agents.md.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Determine Priority (Enforcement Rule 2)
    priority = "Standard"
    found_urgent_word = None
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            found_urgent_word = kw
            break
            
    # 2. Determine Category based on keywords (Enforcement Rule 1 & 4)
    # Rule-based approximation of the classification taxonomy
    category = "Other"
    matched_keyword = None
    
    mapping = {
        "Pothole": ["pothole", "cracked", "hole"],
        "Flooding": ["flood", "water", "rain", "drainage"],
        "Streetlight": ["light", "dark", "lamp", "bulb"],
        "Waste": ["garbage", "trash", "waste", "litter", "smell"],
        "Noise": ["noise", "loud", "sound", "party"],
        "Road Damage": ["road", "pavement", "crack"],
        "Heritage Damage": ["heritage", "monument", "statue", "temple", "church"],
        "Heat Hazard": ["heat", "hot", "fire", "smoke"],
        "Drain Blockage": ["drain", "sewage", "blocked", "clogged"]
    }
    
    for cat, keywords in mapping.items():
        for kw in keywords:
            if kw in description:
                category = cat
                matched_keyword = kw
                break
        if category != "Other":
            break
            
    # 3. Handle Refusal / Ambiguity (Enforcement Rule 4)
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # 4. Generate Reason (Enforcement Rule 3)
    # Must be one sentence and cite specific words.
    if priority == "Urgent":
        reason = f"Priority set to Urgent because the description mentions '{found_urgent_word}'."
    elif category != "Other":
        reason = f"Classified as {category} because the description includes the word '{matched_keyword}'."
    else:
        reason = "The description is ambiguous and does not contain specific keywords for classification."

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
    Ensures the script doesn't crash on bad rows or missing descriptions.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validation: check for required columns
            if not reader.fieldnames or 'description' not in reader.fieldnames:
                print("Error: Input CSV must contain a 'description' column.")
                return
            
            for row in reader:
                # Handle nulls or empty descriptions (Skills requirement)
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "N/A"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Missing or empty description field.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                
                try:
                    results.append(classify_complaint(row))
                except Exception as e:
                    # Robustness: Produce output even if some rows fail
                    results.append({
                        "complaint_id": row.get("complaint_id", "N/A"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Write output to CSV (Skills requirement)
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
