"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json

# Define the allowed categories based on the RICE enforcement
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Define severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get('complaint_id', 'Unknown')
    description = str(row.get('description', '')).lower()
    
    # Error handling / Fallback
    if not description.strip():
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'Invalid or empty input.',
            'flag': 'NEEDS_REVIEW'
        }

    # 1. Determine Priority & Reason
    priority = "Low" # Default
    reason = "No specific severity keywords found."
    
    # Check for urgent keywords
    found_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    if found_keywords:
        priority = "Urgent"
        reason = f"Contains severity keyword(s): {', '.join(found_keywords)}."
    elif "infrastructure" in description or "damage" in description or "broken" in description:
        # Based on agents.md enforcement: Medium/Standard if it affects infrastructure
        priority = "Standard"
        reason = "Mentions infrastructure damage but no immediate danger keywords."

    # 2. Determine Category
    category = "Other"
    
    # Simple keyword heuristic for categorization
    if "pothole" in description or "crater" in description:
        category = "Pothole"
        reason += " Mentions pothole in description."
    elif "flood" in description or "water" in description or "drain" in description:
        # Disambiguate Flooding vs Drain Blockage
        if "block" in description or "clog" in description:
            category = "Drain Blockage"
            reason += " Mentions blocked drains."
        else:
            category = "Flooding"
            reason += " Mentions flooding or standing water."
    elif "light" in description or "dark" in description:
        category = "Streetlight"
        reason += " Mentions lighting issues."
    elif "waste" in description or "garbage" in description or "trash" in description:
        category = "Waste"
        reason += " Mentions waste or garbage."
    elif "noise" in description or "loud" in description:
        category = "Noise"
        reason += " Mentions noise complaints."
    elif "road" in description and "damage" in description:
        category = "Road Damage"
        reason += " Mentions generalized road damage."
    elif "heritage" in description or "monument" in description:
        category = "Heritage Damage"
        reason += " Mentions damage to heritage sites."
    elif "heat" in description or "temperature" in description:
        category = "Heat Hazard"
        reason += " Mentions extreme heat."

    # 3. Determine Flag
    flag = ""
    # Only flag as NEEDS_REVIEW if it truly couldn't be categorized at all
    if category == "Other" and priority != "Low":
        flag = "NEEDS_REVIEW"
        
    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Don't crash on bad rows, produce output
                    results.append({
                        'complaint_id': row.get('complaint_id', 'Unknown'),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f"Processing error: {str(e)}",
                        'flag': 'NEEDS_REVIEW'
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    # Write output CSV
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
