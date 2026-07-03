"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = row.get("complaint_id")
    description = row.get("description", "")

    # Initialize classification with defaults
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    # Define allowed categories and severity keywords
    allowed_categories = [
        "Pothole",
        "Flooding",
        "Streetlight",
        "Waste",
        "Noise",
        "Road Damage",
        "Heritage Damage",
        "Heat Hazard",
        "Drain Blockage",
        "Other",
    ]
    severity_keywords = [
        "injury",
        "child",
        "school",
        "hospital",
        "ambulance",
        "fire",
        "hazard",
        "fell",
        "collapse",
    ]

    # Check for invalid or missing input
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Complaint text is missing or invalid.",
            "flag": "NEEDS_REVIEW",
        }

    # Determine category and reason based on keywords
    # This is a simplified example; a real implementation would use a more sophisticated NLP approach
    if "pothole" in description.lower():
        category = "Pothole"
        reason = "Complaint mentions 'pothole'."
    elif "flood" in description.lower():
        category = "Flooding"
        reason = "Complaint mentions 'flood'."
    elif "streetlight" in description.lower():
        category = "Streetlight"
        reason = "Complaint mentions 'streetlight'."
    elif "waste" in description.lower() or "garbage" in description.lower():
        category = "Waste"
        reason = "Complaint mentions 'waste' or 'garbage'."
    elif "noise" in description.lower():
        category = "Noise"
        reason = "Complaint mentions 'noise'."
    elif "road damage" in description.lower():
        category = "Road Damage"
        reason = "Complaint mentions 'road damage'."
    elif "heritage damage" in description.lower():
        category = "Heritage Damage"
        reason = "Complaint mentions 'heritage damage'."
    elif "heat hazard" in description.lower():
        category = "Heat Hazard"
        reason = "Complaint mentions 'heat hazard'."
    elif "drain blockage" in description.lower():
        category = "Drain Blockage"
        reason = "Complaint mentions 'drain blockage'."
    else:
        category = "Other"
        reason = "Complaint does not clearly fit into predefined categories."
        flag = "NEEDS_REVIEW" # Flag as ambiguous if no clear category

    # Check for severity keywords to assign Urgent priority
    for keyword in severity_keywords:
        if keyword in description.lower():
            priority = "Urgent"
            break

    # Ensure category is from the allowed list (taxonomy drift prevention)
    if category not in allowed_categories:
        category = "Other"
        reason = f"Invalid category detected: {category}. Reverted to Other."
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        complaints = list(reader)

    results = []
    for i, row in enumerate(complaints):
        try:
            classified_row = classify_complaint(row)
            results.append(classified_row)
        except Exception as e:
            # Handle errors in classification for individual rows
            results.append(
                {
                    "complaint_id": row.get("complaint_id", f"UNKNOWN_{i}"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during classification: {e}",
                    "flag": "NEEDS_REVIEW",
                }
            )

    if not results:
        print("No complaints to write or all classifications failed.")
        return

    # Determine fieldnames for the output CSV
    # Ensure all required fields are present
    fieldnames = list(results[0].keys())
    required_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    for field in required_fields:
        if field not in fieldnames:
            fieldnames.append(field)

    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
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
