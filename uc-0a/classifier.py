"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv


def classify_complaint(row: dict) -> dict:
    """
    Classifies a single complaint row into category, priority, reason, and flag according to strict schema rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    # Allowed categories
    categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
        "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    # Severity keywords for Urgent
    urgent_keywords = [
        "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
    ]
    description = (row.get("description") or "").lower()
    complaint_id = row.get("complaint_id", "")
    reason = ""
    flag = ""
    # Category detection (simple keyword-based, can be extended)
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "road": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "block": "Drain Blockage"
    }
    detected_category = None
    for key, value in category_map.items():
        if key in description:
            detected_category = value
            break
    if detected_category is None:
        detected_category = "Other"
        flag = "NEEDS_REVIEW"
    # Priority detection
    priority = "Standard"
    for word in urgent_keywords:
        if word in description:
            priority = "Urgent"
            break
    # Reason: must cite specific words from description
    if detected_category != "Other":
        reason = f"Detected '{detected_category}' from: {description}"
    else:
        reason = f"Category unclear from: {description}"
    # Output dict
    return {
        "complaint_id": complaint_id,
        "category": detected_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }



def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    input_fields = []
    results = []
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        input_fields = reader.fieldnames or []
        for row in reader:
            try:
                # Flag nulls
                if not row.get("description"):
                    result = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Missing description",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    result = classify_complaint(row)
            except Exception as e:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                }
            results.append(result)
    # Write output CSV
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
