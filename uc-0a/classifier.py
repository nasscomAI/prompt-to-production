"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    
    # Priority defaults
    priority = "Standard"
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    triggered_word = next((word for word in urgent_keywords if word in desc), None)
    
    if triggered_word:
        priority = "Urgent"

    # Category matching rules
    category = "Other"
    flag = ""
    
    # Check for specific patterns matching exact required fields
    if "pothole" in desc:
        category = "Pothole"
    elif "drain" in desc:
        category = "Drain Blockage"
    elif "flood" in desc or "knee-deep" in desc:
        category = "Flooding"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
    elif "waste" in desc or "garbage" in desc or "dump" in desc or "animal" in desc:
        category = "Waste"
    elif "noise" in desc or "music" in desc:
        category = "Noise"
    elif "crack" in desc or "tile" in desc or "manhole" in desc or "surface" in desc:
        category = "Road Damage"
    elif "heat" in desc:
        category = "Heat Hazard"
    else:
        flag = "NEEDS_REVIEW"
        
    # Build reason based on matched tokens to satisfy "Must cite specific words"
    reason = "Categorized based on general text matching."
    if priority == "Urgent":
        reason = f"Urgent priority flagged due to severity keyword: '{triggered_word}'."
    elif category != "Other":
        reason = f"Assigned to {category} based on description keywords."
    else:
        reason = "Could not map to specific category, needs review."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                # flag nulls, not crash on bad rows
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description field.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                    
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "ERROR"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    if results:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
