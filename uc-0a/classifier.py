"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine Category
    category = "Other"
    ambiguous = False
    matches = []
    
    if "pothole" in desc: matches.append("Pothole")
    if "flood" in desc: matches.append("Flooding")
    if "streetlight" in desc or "lights out" in desc: matches.append("Streetlight")
    if "garbage" in desc or "waste" in desc or "dead animal" in desc: matches.append("Waste")
    if "music" in desc or "noise" in desc: matches.append("Noise")
    if "road surface" in desc or "footpath" in desc: matches.append("Road Damage")
    if "heritage" in desc: matches.append("Heritage Damage")
    if "drain" in desc or "blocked" in desc: matches.append("Drain Blockage")
    
    if len(matches) == 1:
        category = matches[0]
    elif len(matches) > 1:
        if "drain" in desc and "flood" in desc:
            category = "Flooding" # main category, drain is reason
            ambiguous = True
        else:
            category = matches[0] # Pick first one
            ambiguous = True

    # 2. Determine Priority
    found_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    if found_keywords:
        priority = "Urgent"
        reason = f"Contains severity keyword: '{found_keywords[0]}'."
    else:
        priority = "Standard"
        reason = f"Standard priority for {category}."

    # 3. Determine Flag
    flag = "NEEDS_REVIEW" if ambiguous else ""
        
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
    with open(input_path, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        
        with open(output_path, "w", encoding="utf-8", newline="") as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception as e:
                    writer.writerow({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error parsing: {str(e)}",
                        "flag": "ERROR"
                    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
