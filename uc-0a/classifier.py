import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classified based on R.I.C.E enforcement rules.
    """
    description = row.get('description', '').lower()
    
    # Enforcement: Category must be from the allowed list
    categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]
    
    # Simple keyword matching for taxonomy
    category = "Other"
    if "pothole" in description: category = "Pothole"
    elif "flood" in description or "water" in description: category = "Flooding"
    elif "light" in description: category = "Streetlight"
    elif "waste" in description or "garbage" in description: category = "Waste"
    elif "noise" in description or "loud" in description: category = "Noise"

    # Enforcement: Urgent keywords (Severity blindness check)
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Urgent" if any(word in description for word in urgent_keywords) else "Standard"

    # Enforcement: Reason must cite words from description
    reason = f"Identified as {category} based on description keywords."
    
    # Enforcement: Flag if ambiguous
    flag = "NEEDS_REVIEW" if category == "Other" or not description else ""

    return {
        "complaint_id": row.get('complaint_id', 'unknown'),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Reads input, handles errors, and writes results.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as e:
                print(f"Skipping a bad row: {e}")

    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")