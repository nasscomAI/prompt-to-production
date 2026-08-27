"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Enforcement constants
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row):
    """
    Classifies a single complaint row into category, priority, reason, and flag.
    """
    description = row.get("description", "").lower().strip()
    result = {"category": "", "priority": "Standard", "reason": "", "flag": ""}

    # Error handling: missing description
    if not description:
        result["flag"] = "NEEDS_REVIEW"
        result["reason"] = "Missing description"
        return result

    # Category classification (simple keyword-based mapping)
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "road": "Road Damage",
        "heritage": "Heritage Damage",
        "monument": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "sewage": "Drain Blockage"
    }

    matched_category = None
    for keyword, cat in category_map.items():
        if keyword in description:
            matched_category = cat
            break

    if matched_category and matched_category in ALLOWED_CATEGORIES:
        result["category"] = matched_category
        result["reason"] = f"Matched keyword '{keyword}' in description"
    else:
        # Ambiguous or invalid category
        result["flag"] = "NEEDS_REVIEW"
        result["reason"] = "Ambiguous or no valid category keyword found"

    # Priority classification
    for sev in SEVERITY_KEYWORDS:
        if sev in description:
            result["priority"] = "Urgent"
            if result["reason"]:
                result["reason"] += f"; severity keyword '{sev}' found"
            else:
                result["reason"] = f"Severity keyword '{sev}' found"
            break

    # Ensure reason is always present
    if not result["reason"]:
        result["reason"] = "No clear classification reason"

    return result

def batch_classify(input_file, output_file):
    """
    Reads input CSV, applies classify_complaint to each row, writes output CSV.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} not found")

    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        if "description" not in reader.fieldnames:
            raise ValueError("Input file missing 'description' column")

        results = []
        for row in reader:
            classification = classify_complaint(row)
            results.append({
                "id": row.get("id", ""),
                "category": classification["category"],
                "priority": classification["priority"],
                "reason": classification["reason"],
                "flag": classification["flag"]
            })

    with open(output_file, "w", newline='', encoding='utf-8') as outfile:
        fieldnames = ["id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)

def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
        print(f"Classification complete. Results written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

