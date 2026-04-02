import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row into category, priority, reason, and flag.
    Based on agents.md and skills.md.
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Category
    category = "Other"
    flag = ""
    category_keyword = None
    
    if "pothole" in description:
        category = "Pothole"
        category_keyword = "pothole"
    elif "flood" in description:
        category = "Flooding"
        category_keyword = "flood"
    elif "water" in description:
        category = "Flooding"
        category_keyword = "water"
    elif "streetlight" in description:
        category = "Streetlight"
        category_keyword = "streetlight"
    elif "light" in description:
        category = "Streetlight"
        category_keyword = "light"
    elif "garbage" in description:
        category = "Waste"
        category_keyword = "garbage"
    elif "waste" in description:
        category = "Waste"
        category_keyword = "waste"
    elif "animal" in description:
        category = "Waste"
        category_keyword = "animal"
    elif "music" in description:
        category = "Noise"
        category_keyword = "music"
    elif "noise" in description:
        category = "Noise"
        category_keyword = "noise"
    elif "crack" in description:
        category = "Road Damage"
        category_keyword = "crack"
    elif "sinking" in description:
        category = "Road Damage"
        category_keyword = "sinking"
    elif "manhole" in description:
        category = "Road Damage"
        category_keyword = "manhole"
    elif "footpath" in description:
        category = "Road Damage"
        category_keyword = "footpath"
    elif "heritage" in description:
        category = "Heritage Damage"
        category_keyword = "heritage"
    elif "heat" in description:
        category = "Heat Hazard"
        category_keyword = "heat"
    elif "drain blocked" in description:
        category = "Drain Blockage"
        category_keyword = "drain blocked"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_keyword = None
    
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            found_keyword = kw
            break
            
    if priority != "Urgent" and "minor" in description:
        priority = "Low"

    # 3. Formulate Reason
    if found_keyword:
        reason = f"Classified as Urgent because the description mentions '{found_keyword}'."
    elif category_keyword:
        reason = f"Classified as {category} because the description mentions '{category_keyword}'."
    elif category != "Other":
        reason = f"Main issue matches the {category} category."
    else:
        reason = "The description is ambiguous and could not be clearly categorized."

    return {
        "complaint_id": row.get("complaint_id", "Unknown"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row using the classify_complaint skill, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            # Merge output with original row id (to match expected format)
            results.append({
                "complaint_id": result["complaint_id"],
                "category": result["category"],
                "priority": result["priority"],
                "reason": result["reason"],
                "flag": result["flag"]
            })
        except Exception as e:
            # Output gracefully even if one row fails
            print(f"Error processing row {row.get('complaint_id')}: {e}")
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": "Failed to process",
                "flag": "NEEDS_REVIEW"
            })

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
