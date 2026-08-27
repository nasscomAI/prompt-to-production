"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # Priority keywords from agents.md
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_urgent_word = None
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            found_urgent_word = kw
            break
    
    # Category mapping based on allowed values in README.md / agents.md
    # Categories: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    category = "Other"
    
    if "pothole" in description:
        category = "Pothole"
    elif any(kw in description for kw in ["flood", "water", "underpass", "rain"]):
        category = "Flooding"
        if "drain" in description:
             category = "Drain Blockage"
    elif "streetlight" in description or "light" in description:
        category = "Streetlight"
        if "heritage" in description:
             category = "Heritage Damage"
    elif any(kw in description for kw in ["garbage", "waste", "bins", "dumped", "dead animal"]):
        category = "Waste"
    elif any(kw in description for kw in ["noise", "music", "loud"]):
        category = "Noise"
    elif any(kw in description for kw in ["road", "cracked", "footpath", "tiles", "manhole", "bridge approach"]):
        category = "Road Damage"
    elif "heat" in description:
        category = "Heat Hazard"
    elif "drain" in description:
        category = "Drain Blockage"
    elif "heritage" in description:
        category = "Heritage Damage"
    
    # Reason citing words from description
    if category != "Other":
        reason = f"Classified as {category} based on the description contents."
        if priority == "Urgent" and found_urgent_word:
            reason = f"Priority is Urgent because description contains '{found_urgent_word}'."
    else:
        reason = "Ambiguous description; could not determine specific category."
    
    # Flag set to NEEDS_REVIEW when ambiguous
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                classified = classify_complaint(row)
                results.append(classified)
        
        if not results:
            print("No data found in input CSV.")
            return

        # Ensure fieldnames match expected output schema
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"An error occurred during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
