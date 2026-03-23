"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            break
            
    category = "Other"
    flag = "NEEDS_REVIEW"
    
    if "pothole" in desc: category = "Pothole"; flag = ""
    elif "flood" in desc or "water" in desc: category = "Flooding"; flag = ""
    elif ("light" in desc or "dark" in desc) and "heritage" not in desc: category = "Streetlight"; flag = ""
    elif "waste" in desc or "garbage" in desc or "animal" in desc or "smell" in desc: category = "Waste"; flag = ""
    elif "music" in desc or "noise" in desc: category = "Noise"; flag = ""
    elif "road" in desc or "crack" in desc or "tile" in desc: category = "Road Damage"; flag = ""
    elif "heritage" in desc: category = "Heritage Damage"; flag = ""
    elif "heat" in desc: category = "Heat Hazard"; flag = ""
    elif "drain" in desc or "manhole" in desc: category = "Drain Blockage"; flag = ""

    reason = "No specific keyword found."
    if priority == "Urgent":
        for kw in SEVERITY_KEYWORDS:
            if kw in desc:
                reason = f"The description mentions '{kw}' making it an Urgent {category}."
                break
    else:
        reason = f"Classified based on description details."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8', newline='') as fout:
        reader = csv.DictReader(fin)
        existing_fields = reader.fieldnames or []
        fieldnames = [*existing_fields, "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            res = classify_complaint(row)
            row.update(res)
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
