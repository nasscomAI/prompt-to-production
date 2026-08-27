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
    Implements the schema and enforcement rules from agents.md and skills.md.
    """
    # Allowed categories
    CATEGORIES = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
        "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    SEVERITY_KEYWORDS = [
        "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
    ]
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")
    # Simple rules for demo: match keywords to category
    category = "Other"
    reason = ""
    flag = ""
    desc_lower = description.lower()
    # Category heuristics (expand as needed)
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
        "blockage": "Drain Blockage",
        "damage": "Road Damage",
    }
    for k, v in category_map.items():
        if k in desc_lower:
            category = v
            break
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Category ambiguous; no clear match in description."
    else:
        reason = f"Description contains keyword(s): {', '.join([k for k in category_map if k in desc_lower])}"
    # Priority
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in desc_lower:
            priority = "Urgent"
            reason += f" Severity keyword: {word}."
            break
    # If description is empty
    if not description:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Missing description."
        priority = "Standard"
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    input_fields = None
    results = []
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        input_fields = reader.fieldnames
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as e:
                # On error, flag row for review
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                }
            results.append(result)
    # Write output
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
