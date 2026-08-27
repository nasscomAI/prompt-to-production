"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Priority
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in description:
            priority = "Urgent"
            break
            
    # Category and Flag (Keyword Matching)
    category = "Other"
    flag = ""
    reason = "No specific category matched."
    matches = []
    
    if "pothole" in description:
        matches.append("Pothole")
    if "flood" in description or "water" in description:
        matches.append("Flooding")
    if "streetlight" in description or "dark" in description or "spark" in description:
        matches.append("Streetlight")
    if "waste" in description or "garbage" in description or "dead animal" in description:
        matches.append("Waste")
    if "music" in description or "noise" in description:
        matches.append("Noise")
    if "road surface" in description or "crack" in description or "manhole" in description:
        matches.append("Road Damage")
    if "heritage" in description:
        matches.append("Heritage Damage")
    if "heat" in description:
        matches.append("Heat Hazard")
    if "drain blocked" in description:
        matches.append("Drain Blockage")
        
    if len(matches) == 1:
        category = matches[0]
        reason = f"Matches '{category}' related keywords."
    elif len(matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous matching multiple categories: {matches}."
    else:
        # Fallback reason
        reason = "Did not match any specific category keywords."
        if priority == "Urgent":
            flag = "NEEDS_REVIEW"

    # Specific override for missing manhole
    if "manhole cover missing" in description:
        category = "Road Damage"
        reason = "Mentioned missing manhole cover."

    # Return required fields
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = list(reader.fieldnames)
        
    for new_col in ["category", "priority", "reason", "flag"]:
        if new_col not in fieldnames:
            fieldnames.append(new_col)
            
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            try:
                result = classify_complaint(row)
                row.update(result)
                writer.writerow(row)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id')}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
