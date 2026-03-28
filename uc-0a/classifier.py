"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on fixed taxonomy and urgency rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Category Mapping
    category = "Other"
    flag = ""
    
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description or "waterlogging" in description:
        category = "Flooding"
    elif "streetlight" in description or "unlit" in description or "wiring" in description:
        category = "Streetlight"
    elif "waste" in description or "garbage" in description or "bins" in description:
        category = "Waste"
    elif "noise" in description or "music" in description or "loud" in description:
        category = "Noise"
    elif "road damage" in description or "subsidence" in description or "tarmac" in description or "surface" in description:
        if "heritage" in description or "ancient" in description:
            category = "Heritage Damage"
        else:
            category = "Road Damage"
    elif "heritage" in description or "ancient" in description:
        category = "Heritage Damage"
    elif "heat" in description or "temperature" in description or "44°c" in description or "45°c" in description or "heatwave" in description:
        category = "Heat Hazard"
    elif "drain" in description or "blockage" in description:
        category = "Drain Blockage"
    
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # 2. Priority Rules
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            break
    
    if row.get("days_open") and int(row.get("days_open", 0)) > 14 and priority != "Urgent":
        priority = "Standard" # Default
    
    # 3. Reason (One sentence citing words)
    reason = f"Classified as {category} because description mentions '{description.split('.')[0]}'."
    if priority == "Urgent":
        triggered = [kw for kw in severity_keywords if kw in description]
        reason = f"Urgent priority assigned due to mentioned safety risk: '{triggered[0]}'. Category {category} determined from description."

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
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
        
        if not results:
            print("No data to write.")
            return

        keys = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
    except Exception as e:
        print(f"Batch processing failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
