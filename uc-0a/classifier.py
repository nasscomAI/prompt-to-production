"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    category = "Other"
    flag = ""
    found_categories = []
    
    if "pothole" in description:
        found_categories.append("Pothole")
    if "flood" in description:
        found_categories.append("Flooding")
    if "streetlight" in description or "lights out" in description or "dark" in description:
        found_categories.append("Streetlight")
    if "garbage" in description or "waste" in description or "dead animal" in description:
        found_categories.append("Waste")
    if "music" in description or "noise" in description:
        found_categories.append("Noise")
    if "road surface" in description or "cracked" in description or "manhole" in description or "footpath" in description:
        found_categories.append("Road Damage")
    if "heritage" in description:
        found_categories.append("Heritage Damage")
    if "drain blocked" in description:
        found_categories.append("Drain Blockage")
        
    if len(found_categories) == 1:
        category = found_categories[0]
    elif len(found_categories) > 1:
        if "Flooding" in found_categories and "Drain Blockage" in found_categories:
            category = "Flooding"
        elif "Streetlight" in found_categories and "Heritage Damage" in found_categories:
            category = "Heritage Damage"
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    priority = "Standard"
    urgent_keywords_found = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    if urgent_keywords_found:
        priority = "Urgent"
        
    if urgent_keywords_found:
        reason = f"Classified as {category} and Urgent due to keywords: {', '.join(urgent_keywords_found)}."
    elif category != "Other":
        reason = f"Classified as {category} based on description keywords."
    else:
        reason = "Could not confidently classify category."

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
    with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8", newline="") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error formatting row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

