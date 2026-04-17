"""
UC-0A — Complaint Classifier
Implemented based on RICE (agents.md) and skills.md.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based logic derived from agents.md.
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Category
    category = "Other"
    if "pothole" in description:
        category = "Pothole"
    elif any(word in description for word in ["flood", "waterlogging", "rain water"]):
        category = "Flooding"
    elif any(word in description for word in ["streetlight", "unlit", "dark", "wiring"]):
        category = "Streetlight"
    elif any(word in description for word in ["waste", "garbage", "bin", "overflowing"]):
        category = "Waste"
    elif any(word in description for word in ["noise", "music", "loud"]):
        category = "Noise"
    elif any(word in description for word in ["road damage", "tarmac", "subsidence", "surface"]):
        if "step well" in description or "heritage" in description:
            category = "Heritage Damage"
        elif "heat" in description or "melting" in description or "bubbling" in description:
            category = "Heat Hazard"
        else:
            category = "Road Damage"
    elif any(word in description for word in ["drain", "blockage", "sewage"]):
        category = "Drain Blockage"
    elif any(word in description for word in ["ancient", "heritage", "monument"]):
        category = "Heritage Damage"
    
    # 2. Determine Priority based on severity keywords
    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse", "dangerous", "unsafe"
    ]
    
    priority = "Standard"
    triggered_word = None
    for word in severity_keywords:
        if word in description:
            priority = "Urgent"
            triggered_word = word
            break
            
    # 3. Generate Reason
    if category != "Other":
        reason = f"Classified as {category} because description mentions '{next((w for w in category.lower().split() if w in description), category.lower())}'."
        if priority == "Urgent":
            reason += f" Priority set to Urgent due to safety risk ('{triggered_word}')."
    else:
        reason = "Placed in Other category as it does not clearly map to specific taxonomy."

    # 4. Set Flag for ambiguity
    flag = "NEEDS_REVIEW" if category == "Other" or "ambiguous" in description else ""

    return {
        "complaint_id": row.get("complaint_id"),
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

    try:
        results = []
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Skipping row {row.get('complaint_id')}: {e}")

        if not results:
            print("No results to write.")
            return

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print(f"Batch processing failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
