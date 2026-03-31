import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the constraints defined in agents.md.
    """
    desc = row.get("description", "").strip()
    desc_lower = desc.lower()

    # Determine Category based on rules and keywords
    category = "Other"
    
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower or "rain" in desc_lower:
        category = "Flooding"
    elif "streetlight" in desc_lower or "dark" in desc_lower or "spark" in desc_lower:
        category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "dead animal" in desc_lower or "dumped" in desc_lower:
        category = "Waste"
    elif "music" in desc_lower or "noise" in desc_lower:
        category = "Noise"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
    elif "road surface" in desc_lower or "crack" in desc_lower or "sinking" in desc_lower or "broken" in desc_lower:
        if category == "Other":
            category = "Road Damage"
    elif "drain" in desc_lower or "manhole" in desc_lower:
        category = "Drain Blockage"
    elif "heat" in desc_lower:
        category = "Heat Hazard"
        
    flag = ""
    # "If the category cannot be explicitly determined or is genuinely ambiguous..."
    # A manhole cover missing could be a road hazard or drain issue.
    if "manhole cover missing" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Determine Priority
    # Urgent if severity keywords present
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            break

    # Determine Reason
    # Exactly one sentence citing specific words. We can extract the sentence that triggered the category or priority.
    # Split by basic sentence terminators.
    sentences = [s.strip() for s in re.split(r'[.!?]', desc) if s.strip()]
    reason = sentences[0] + "." if sentences else "Issue reported without substantial description."

    if flag == "NEEDS_REVIEW":
        reason += " Categorization ambiguous."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must handle bad rows and produce output.
    """
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    print(f"Skipping malformed row {row.get('complaint_id', 'UNKNOWN')}: {e}")
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_path}")
        return

    if not results:
        print("No valid rows processed.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
