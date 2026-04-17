"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    if not desc:
        desc = ""
    desc_lower = desc.lower()
    
    # Predefined valid categories mapping based on enforcement rules
    categories_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "music": "Noise",
        "road damage": "Road Damage",
        "crack": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage"
    }
    
    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    
    # 1. Determine Category
    matched_cat = None
    for keyword, cat in categories_map.items():
        if keyword in desc_lower:
            matched_cat = cat
            break
            
    if matched_cat:
        category = matched_cat
        flag = ""
    else:
        # Ambiguous classification
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 2. Determine Priority
    priority = "Standard"
    matched_severity = None
    for keyword in severity_keywords:
        if keyword in desc_lower:
            priority = "Urgent"
            matched_severity = keyword
            break
            
    # 3. Determine Reason
    if priority == "Urgent":
        reason = f"Priority is Urgent because the description mentions the severity keyword '{matched_severity}'."
    elif category != "Other":
        matched_word = [k for k in categories_map.keys() if k in desc_lower][0]
        reason = f"Classified as {category} because the description mentions '{matched_word}'."
    else:
        reason = "Category could not be confidently determined from the description."
        
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # Flag nulls
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Description is missing or null.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    # Do not crash on bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error during classification: {str(e)}",
                        "flag": "ERROR"
                    })
    except Exception as e:
        print(f"Failed to read input file {input_path}: {e}")
        return
        
    if not results:
        print("No rows to write.")
        return
        
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
