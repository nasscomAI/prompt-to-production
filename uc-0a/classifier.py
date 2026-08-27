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
    Implements RICE enforcement rules from agents.md and skills.md.
    """
    allowed_categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
        "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    urgent_keywords = [
        "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
    ]
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")
    category = "Other"
    flag = ""
    reason = ""
    priority = "Standard"

    if not description:
        reason = "No description provided."
        flag = "NEEDS_REVIEW"
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }

    desc_lower = description.lower()
    # Category detection (simple keyword mapping)
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "waterlogging": "Flooding",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "trash": "Waste",
        "noise": "Noise",
        "loud": "Noise",
        "road": "Road Damage",
        "crack": "Road Damage",
        "damage": "Road Damage",
        "heritage": "Heritage Damage",
        "monument": "Heritage Damage",
        "heat": "Heat Hazard",
        "hot": "Heat Hazard",
        "drain": "Drain Blockage",
        "block": "Drain Blockage",
        "clog": "Drain Blockage"
    }
    found_category = None
    for k, v in category_map.items():
        if k in desc_lower:
            found_category = v
            break
    if found_category and found_category in allowed_categories:
        category = found_category
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority detection
    if any(word in desc_lower for word in urgent_keywords):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Reason field
    if found_category:
        reason = f"Description contains '{k}' indicating category '{category}'."
    else:
        reason = "Category could not be determined from description."
    # If urgent, append justification
    for word in urgent_keywords:
        if word in desc_lower:
            reason += f" Marked Urgent due to presence of '{word}'."
            break

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
    results = []
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as e:
                # Fallback for row-level error
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                }
            results.append(result)

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
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
