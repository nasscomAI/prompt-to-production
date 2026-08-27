"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Rule: Priority must be Urgent if severity keywords present
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_severity = [kw for kw in severity_keywords if kw in description]
    
    if found_severity:
        priority = "Urgent"
        priority_reason = f"Contains severity keyword(s): {', '.join(found_severity)}."
    else:
        priority = "Standard"
        priority_reason = "No severity keywords detected."

    # Rule: Map description to strict categories
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "rain": "Flooding",
        "water": "Flooding",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "dark": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "smell": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "crack": "Road Damage",
        "sink": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage"
    }
    
    found_categories = []
    category_reasons = []
    for kw, cat in category_map.items():
        if kw in description and cat not in found_categories:
            found_categories.append(cat)
            category_reasons.append(f"Mentions '{kw}'.")
            
    # Rule: Flag ambiguous or unknown classifications
    flag = ""
    if len(found_categories) == 1:
        category = found_categories[0]
        reason = f"Classified as {category} because description {category_reasons[0]} {priority_reason}"
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous category. Matches multiple: {', '.join(found_categories)}. {priority_reason}"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Cannot determine category from description alone. {priority_reason}"

    # Construct the correct output dictionary
    output = dict(row)
    output["category"] = category
    output["priority"] = priority
    output["reason"] = reason
    output["flag"] = flag
    
    return output


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    writer.writerow(classified_row)
                except Exception as e:
                    # Append empty classification on failure to ensure system doesn't crash
                    failed_row = dict(row)
                    failed_row["category"] = ""
                    failed_row["priority"] = ""
                    failed_row["reason"] = f"Error during classification: {str(e)}"
                    failed_row["flag"] = "ERROR"
                    writer.writerow(failed_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
