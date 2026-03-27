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
    Implements agent and skill rules from agents.md and skills.md.
    """
    allowed_categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
        "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
    ]
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "").strip()
    flag = ""

    # Category classification (simple keyword-based, can be improved)
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "noise": "Noise",
        "road": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "manhole": "Drain Blockage",
        "animal": "Waste",
        "crack": "Road Damage",
        "tile": "Road Damage",
        "footpath": "Road Damage",
        "bridge": "Road Damage",
        "market": "Waste",
        "music": "Noise",
        "wedding": "Noise",
        "depression": "Road Damage",
        "heritage street": "Heritage Damage",
    }
    category = None
    desc_lower = description.lower()
    for key, value in category_map.items():
        if key in desc_lower:
            category = value
            break
    if not category:
        # Try to match by allowed categories directly
        for cat in allowed_categories:
            if cat.lower() in desc_lower:
                category = cat
                break
    if not category:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority assignment
    priority = "Standard"
    for word in severity_keywords:
        if word in desc_lower:
            priority = "Urgent"
            break
    # If not urgent, optionally set Low for some cases (not required by schema, so default Standard)

    # Reason: must cite specific words from description
    reason = ""
    if category != "Other":
        # Use a phrase from the description that matches the category
        for key in category_map.keys():
            if key in desc_lower:
                # Find the sentence or phrase containing the keyword
                idx = desc_lower.find(key)
                snippet = description[max(0, idx-20):idx+40]
                reason = f"Cites '{key}' in: {snippet.strip()}"
                break
        if not reason:
            reason = f"Category inferred from: {description[:60]}"
    else:
        reason = f"Ambiguous: {description[:60]}"

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
                # Check for nulls in required fields
                if not row.get("complaint_id") or not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Missing required fields.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
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
