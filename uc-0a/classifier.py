"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    text = row.get("description", "").lower()

    category = "Other"
    priority = "Low"
    flag = ""
    reason = ""

    # Category detection
    if "pothole" in text:
        category = "Pothole"
        reason = "contains word pothole"
    elif "flood" in text or "waterlogging" in text:
        category = "Flooding"
        reason = "contains word flood/waterlogging"
    elif "light" in text:
        category = "Streetlight"
        reason = "contains word light"
    elif "garbage" in text or "waste" in text:
        category = "Waste"
        reason = "contains word garbage/waste"
    elif "noise" in text:
        category = "Noise"
        reason = "contains word noise"
    elif "road" in text or "damage" in text:
        category = "Road Damage"
        reason = "contains word road/damage"
    elif "drain" in text:
        category = "Drain Blockage"
        reason = "contains word drain"
    elif "heat" in text:
        category = "Heat Hazard"
        reason = "contains word heat"
    elif "heritage" in text:
        category = "Heritage Damage"
        reason = "contains word heritage"

    # Priority detection
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

    if any(word in text for word in urgent_keywords):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Ambiguity check
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "unclear category from description"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception:
            result = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": "error processing row",
                "flag": "NEEDS_REVIEW"
            }
        results.append(result)

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
