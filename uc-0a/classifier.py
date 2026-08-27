"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Allowed categories and severity keywords
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
}

def classify_complaint(description: str):
    """
    Classifies a single complaint row into category, priority, reason, and flag.
    """
    desc_lower = description.lower()

    # --- Category detection (simple keyword-based) ---
    category = None
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower or "waterlogging" in desc_lower:
        category = "Flooding"
    elif "streetlight" in desc_lower or "lamp" in desc_lower:
        category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "trash" in desc_lower:
        category = "Waste"
    elif "noise" in desc_lower or "loud" in desc_lower:
        category = "Noise"
    elif "road" in desc_lower or "highway" in desc_lower:
        category = "Road Damage"
    elif "heritage" in desc_lower or "monument" in desc_lower:
        category = "Heritage Damage"
    elif "heat" in desc_lower or "hot" in desc_lower:
        category = "Heat Hazard"
    elif "drain" in desc_lower or "sewage" in desc_lower:
        category = "Drain Blockage"
    else:
        category = "Other"

    # --- Priority detection ---
    priority = "Standard"
    for keyword in SEVERITY_KEYWORDS:
        if keyword in desc_lower:
            priority = "Urgent"
            break

    # --- Reason generation ---
    words = description.split()
    reason = f"Complaint mentions: {' '.join(words[:5])}..."

    # --- Error handling & flagging ---
    flag = ""
    if category not in ALLOWED_CATEGORIES:
        flag = "NEEDS_REVIEW"
    if not reason or len(reason.strip()) == 0:
        reason = "Reason cites complaint text."
    if category == "Other" and len(desc_lower.strip()) < 10:
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_file: str, output_file: str):
    """
    Reads input CSV, applies classify_complaint per row, writes output CSV.
    """
    results = []
    with open(input_file, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            description = row.get("description", "")
            classified = classify_complaint(description)
            results.append(classified)

    # Write output CSV
    with open(output_file, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found.")
        return

    batch_classify(args.input, args.output)
    print(f"Classification complete. Results written to {args.output}")

if __name__ == "__main__":
    main()

