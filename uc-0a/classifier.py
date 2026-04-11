import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint
    One complaint row in -> category + priority + reason + flag out.
    Enforces exact taxonomy and severity-based prioritization.
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Category (Enforcement: Exact strings only)
    category = "Other"
    category_keyword = None
    flag = ""

    # Mapping based on README schema
    if "pothole" in description:
        category, category_keyword = "Pothole", "pothole"
    elif any(kw in description for kw in ["flood", "water"]):
        category, category_keyword = "Flooding", "flood" if "flood" in description else "water"
    elif any(kw in description for kw in ["streetlight", "light"]):
        category, category_keyword = "Streetlight", "light"
    elif any(kw in description for kw in ["garbage", "waste", "trash", "animal"]):
        category, category_keyword = "Waste", "waste"
    elif any(kw in description for kw in ["noise", "music", "loud"]):
        category, category_keyword = "Noise", "noise"
    elif any(kw in description for kw in ["crack", "sinking", "manhole", "footpath", "road damage"]):
        category, category_keyword = "Road Damage", "road damage"
    elif "heritage" in description:
        category, category_keyword = "Heritage Damage", "heritage"
    elif "heat" in description:
        category, category_keyword = "Heat Hazard", "heat"
    elif "drain" in description:
        category, category_keyword = "Drain Blockage", "drain"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority (Enforcement: Severity keywords trigger Urgent)
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_severity = None
    
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            found_severity = kw
            break
            
    if priority != "Urgent" and "minor" in description:
        priority = "Low"

    # 3. Formulate Reason (Enforcement: One sentence, cite specific words)
    if not description:
        reason = "No description provided."
    elif found_severity:
        reason = f"Classified as Urgent because the description mentions '{found_severity}'."
    elif category_keyword:
        reason = f"Classified as {category} because the description mentions '{category_keyword}'."
    else:
        reason = "The description is ambiguous and could not be clearly categorized."

    return {
        "complaint_id": row.get("complaint_id", "Unknown"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Skill: batch_classify
    Reads input CSV, applies classify_complaint per row, writes output CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # Skill application + Error Handling
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    print(f"Row error: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "Error"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Failed to process row logic",
                        "flag": "NEEDS_REVIEW"
                    })

        # Output logic as per UC README
        os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
        
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Batch processing error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
