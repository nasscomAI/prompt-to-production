"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "pothole", "tyre damage", "tyre"],
    "Flooding": ["flood", "flooded", "flooding", "knee-deep", "water logged", "waterlogged"],
    "Streetlight": ["streetlight", "street light", "lights out", "flickering", "sparking", "dark at night"],
    "Waste": ["garbage", "waste", "overflowing", "dumped", "dead animal", "not removed"],
    "Noise": ["noise", "music", "loud", "midnight", "playing music"],
    "Road Damage": ["road surface", "cracked", "sinking", "road damaged", "footpath", "broken", "upturned"],
    "Heritage Damage": ["heritage", "old city", "heritage street"],
    "Heat Hazard": ["heat", "hot", "temperature"],
    "Drain Blockage": ["drain blocked", "drain", "manhole", "sewer"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # Classify category
    category = "Other"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                break
        if category != "Other":
            break

    # Classify priority
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break

    # Generate reason citing specific words
    reason = f"Classified as {category} based on description containing relevant keywords."

    # Set flag for ambiguous cases
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

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
    """
    results = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                print(f"Warning: Skipping row {row.get('complaint_id', 'unknown')}: {e}")
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
