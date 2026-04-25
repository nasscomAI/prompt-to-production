"""
UC-0A — Complaint Classifier
Implementation guided by RICE (agents.md) and skills.md.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint based on its text description.
    Enforces rules defined in agents.md.
    """
    description = row.get("description", "").strip().lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # Rule: If description is missing set flag: NEEDS_REVIEW and category: Other.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The description field was empty or missing.",
            "flag": "NEEDS_REVIEW"
        }

    # Taxonomy and Keyword Mapping
    taxonomy = {
        "Pothole": ["pothole", "cracked", "hole"],
        "Flooding": ["flood", "water", "inundated", "submerged"],
        "Streetlight": ["light", "bulb", "dark", "lamp"],
        "Waste": ["garbage", "trash", "waste", "rubbish", "dump"],
        "Noise": ["loud", "noise", "sound", "volume"],
        "Road Damage": ["pavement", "broken road", "asphalt"],
        "Heritage Damage": ["heritage", "statue", "monument", "historic"],
        "Heat Hazard": ["heat", "hot", "temperature", "sunstroke"],
        "Drain Blockage": ["drain", "sewage", "clogged", "gutter"]
    }

    category = "Other"
    reason_cite = ""
    flag = ""

    # Simple Keyword matching for category
    for cat, keywords in taxonomy.items():
        for kw in keywords:
            if kw in description:
                category = cat
                reason_cite = kw
                break
        if category != "Other":
            break

    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason_cite = "no matching category found"
        reason = f"Classified as Other because {reason_cite} in description."
    else:
        reason = f"Classified as {category} based on the mention of '{reason_cite}' in the description."

    # Priority Enforcement Rule:
    # "Priority must be Urgent if description contains words like injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            reason += f" Priority set to Urgent due to safety keyword: '{kw}'."
            break
            
    # Default to Low for some cases or keep Standard
    if priority == "Standard" and category == "Other":
        priority = "Low"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, processes each row, and writes results to a new CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    # Ensure we still have a basic entry even on failure
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Internal processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

        if not results:
            print("No data processed.")
            return

        # Write results
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print(f"Critical error during batch processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
