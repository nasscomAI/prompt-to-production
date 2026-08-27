"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
(Modified for local rule-based simulation since no API key is provided)
"""
import argparse
import csv

# Local mock classification logic to replace the LLM since no API key is provided
def local_mock_classify(description: str) -> dict:
    desc_lower = description.lower()
    
    # 1. Determine Category
    category = "Other"
    if "pothole" in desc_lower: category = "Pothole"
    elif "flood" in desc_lower or "rain" in desc_lower: category = "Flooding"
    elif "light" in desc_lower or "dark" in desc_lower: category = "Streetlight"
    elif "garbage" in desc_lower or "waste" in desc_lower or "smell" in desc_lower: category = "Waste"
    elif "music" in desc_lower or "noise" in desc_lower: category = "Noise"
    elif "crack" in desc_lower or "surface" in desc_lower or "road" in desc_lower or "footpath" in desc_lower: category = "Road Damage"
    elif "heritage" in desc_lower: category = "Heritage Damage"
    elif "heat" in desc_lower: category = "Heat Hazard"
    elif "drain" in desc_lower or "manhole" in desc_lower: category = "Drain Blockage"
    
    # 2. Determine Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in urgent_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            break
            
    # 3. Determine Flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # 4. Determine Reason
    reason = f"Classified as {category} based on keywords in description."
    if priority == "Urgent":
        reason += " Marked Urgent due to severity keywords."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on skills.md and agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # error_handling fallback defined in skills.md
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty.",
            "flag": "NEEDS_REVIEW"
        }

    try:
        # Using local mock instead of LLM
        result = local_mock_classify(description)
        
        return {
            "complaint_id": complaint_id,
            "category": result.get("category", "Other"),
            "priority": result.get("priority", "Low"),
            "reason": result.get("reason", ""),
            "flag": result.get("flag", "")
        }
    except Exception as e:
        print(f"Error classifying {complaint_id}: {e}")
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": f"Error during classification: {str(e)}",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV of complaints, apply the classify_complaint skill to each row, 
    and write the structured results to an output CSV.
    """
    results = []
    
    print(f"Reading input from {input_path}")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(f"Processing {row.get('complaint_id')}...")
                classification = classify_complaint(row)
                results.append(classification)
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return

    print(f"Writing {len(results)} results to {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            if not results:
                print("No results to write.")
                return
                
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Error writing output CSV: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
