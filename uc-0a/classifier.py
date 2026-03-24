"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules in agents.md.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    # Define allowed categories
    categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
                  "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"]
    
    # Simple keyword-based category matching (simulating an agent's logic)
    category = "Other"
    for cat in categories:
        if cat.lower() in description or cat.lower().replace(" ", "") in description:
            category = cat
            break
            
    # Priority rules
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    urgent_found = [word for word in urgent_keywords if word in description]
    if urgent_found:
        priority = "Urgent"
    
    # Reason rule: One sentence, cite words
    if category != "Other":
        reason = f"Classified as {category} because the description mentions '{category.lower()}'. "
    else:
        reason = "Classified as Other because no specific category keywords were identified. "
    
    if urgent_found:
        reason += f"Priority set to Urgent due to safety-critical keyword(s): {', '.join(urgent_found)}."
    else:
        reason += "Priority set to Standard as no immediate life-safety keywords were detected."

    # Flag rule
    flag = ""
    if category == "Other" or not description:
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
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id')}: {e}")
                    # Follow skills.md: log and continue
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification failed: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    if not results:
        print("No results to write.")
        return

    keys = results[0].keys()
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
