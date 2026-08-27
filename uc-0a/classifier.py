"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Allowed categories
    categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    
    # Severity keywords for Urgent priority
    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    
    # 1. Determine Priority
    priority = "Standard"
    matched_severity = [kw for kw in severity_keywords if kw in description]
    if matched_severity:
        priority = "Urgent"
    elif any(kw in description for kw in ["minor", "slow", "annoyance"]):
        priority = "Low"
        
    # 2. Determine Category (Rule-based heuristic for starter)
    category = "Other"
    reason_word = ""
    
    mapping = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "water logging": "Flooding",
        "light": "Streetlight",
        "lamp": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "loud": "Noise",
        "road": "Road Damage",
        "crack": "Road Damage",
        "heritage": "Heritage Damage",
        "monument": "Heritage Damage",
        "heat": "Heat Hazard",
        "hot": "Heat Hazard",
        "drain": "Drain Blockage",
        "sewage": "Drain Blockage"
    }
    
    for kw, cat in mapping.items():
        if kw in description:
            category = cat
            reason_word = kw
            break
            
    # 3. Handle Flag for ambiguity
    flag = ""
    if category == "Other" or not description:
        flag = "NEEDS_REVIEW"
        
    # 4. Generate Reason (One sentence, citing words)
    if not description:
        reason = "Empty description provided."
    elif category != "Other":
        reason = f"Classified as {category} because the description mentions '{reason_word}'."
    else:
        reason = "Category could not be determined from the description alone."
        
    if priority == "Urgent" and matched_severity:
        reason += f" Priority set to Urgent due to keyword '{matched_severity[0]}'."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames or "description" not in fieldnames:
                print(f"Error: Input CSV at {input_path} must have a 'description' column.")
                return

            for row in reader:
                classification = classify_complaint(row)
                # Combine original row with classification results
                row.update(classification)
                results.append(row)
                
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    if not results:
        print("No data to write.")
        return

    # Prepare output fieldnames
    output_fields = list(results[0].keys())
    
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
