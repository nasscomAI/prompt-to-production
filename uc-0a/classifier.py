"""
UC-0A — Complaint Classifier
Completed using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on agents.md enforcement rules.
    """
    description = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', 'unknown')
    
    # 1. CATEGORY ENFORCEMENT (Strict Taxonomy)
    # Rules: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, 
    # Heritage Damage, Heat Hazard, Drain Blockage, Other
    category = "Other"
    if "pothole" in description: category = "Pothole"
    elif "flood" in description or "water logging" in description: category = "Flooding"
    elif "light" in description or "dark" in description: category = "Streetlight"
    elif "garbage" in description or "waste" in description: category = "Waste"
    elif "noise" in description or "loud" in description: category = "Noise"
    elif "road" in description and "damage" in description: category = "Road Damage"
    elif "drain" in description: category = "Drain Blockage"
    elif "heritage" in description or "monument" in description: category = "Heritage Damage"
    elif "heat" in description or "sun" in description: category = "Heat Hazard"

    # 2. PRIORITY ENFORCEMENT (Urgent Keywords)
    priority = "Standard"
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    if any(keyword in description for keyword in urgent_keywords):
        priority = "Urgent"
    elif "minor" in description or "low" in description:
        priority = "Low"

    # 3. REASONING (Must cite words)
    # Finding which keyword triggered the category or priority
    reason = f"Classified as {category} because description mentions relevant keywords."
    if priority == "Urgent":
        triggered = [w for w in urgent_keywords if w in description]
        reason = f"Urgent priority assigned due to safety keywords: {', '.join(triggered)}."

    # 4. AMBIGUITY FLAG
    flag = "NEEDS_REVIEW" if category == "Other" or not description.strip() else ""

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
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                # Process each row
                classified_data = classify_complaint(row)
                results.append(classified_data)
            except Exception as e:
                print(f"Skipping a bad row: {e}")

    # Write the results to CSV
    if results:
        keys = results[0].keys()
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
    else:
        print("No data processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"✅ Done. Results written to {args.output}")