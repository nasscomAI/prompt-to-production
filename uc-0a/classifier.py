"""
UC-0A — Complaint Classifier
Built using AI-assisted classification with RICE enforcement rules.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()

    # Determine category
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description:
        category = "Flooding"
    elif "streetlight" in description or "light" in description:
        category = "Streetlight"
    elif "waste" in description or "garbage" in description or "trash" in description:
        category = "Waste"
    elif "noise" in description or "drilling" in description or "idling" in description:
        category = "Noise"
    elif "road" in description and "collaps" in description:
        category = "Road Damage"
    elif "heritage" in description or "historical" in description:
        category = "Heritage Damage"
    elif "heat" in description:
        category = "Heat Hazard"
    elif "drain" in description or "drain blocked" in description or "stormwater" in description:
        category = "Drain Blockage"
    else:
        category = "Other"

    # Determine priority
    priority = "Standard"
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = "Urgent"
            break
    if int(row.get("days_open", 0)) > 15:
        priority = "Urgent"

    # Generate reason
    reason = f"Classified as {category} based on description mentioning key terms."

    # Flag ambiguous cases
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "unknown"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during classification: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")