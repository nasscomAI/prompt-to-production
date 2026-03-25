"""
UC-0A — Complaint Classifier
Generated using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
import re

# RICE Context: Fixed allowed categories
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# RICE Enforcement: Severity keywords for Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not row or "description" not in row or not row["description"].strip():
        # Skill Error Handling: if input is null or unreadable
        return {
            "complaint_id": row.get("complaint_id", "UNKNOWN"),
            "category": "Other",
            "priority": "Low",
            "reason": "Input is null or unreadable.",
            "flag": "NEEDS_REVIEW"
        }

    description = row["description"]
    desc_lower = description.lower()
    
    # RICE Enforcement: Priority must be Urgent if severity keywords present
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break
            
    # Simple algorithmic categorization based on description keywords
    determined_category = "Other"
    
    if "pothole" in desc_lower:
        determined_category = "Pothole"
    elif "flood" in desc_lower or "rain" in desc_lower:
        determined_category = "Flooding"
    elif "streetlight" in desc_lower or "dark" in desc_lower:
        determined_category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "animal" in desc_lower:
        determined_category = "Waste"
    elif "music" in desc_lower or "noise" in desc_lower:
        determined_category = "Noise"
    elif "manhole" in desc_lower:
        determined_category = "Drain Blockage"
    elif "heritage" in desc_lower and "damage" in desc_lower:
        determined_category = "Heritage Damage"
    elif "heat" in desc_lower:
        determined_category = "Heat Hazard"
    elif "drain" in desc_lower:
        determined_category = "Drain Blockage"
    elif "road" in desc_lower or "crack" in desc_lower or "sink" in desc_lower or "broken" in desc_lower or "tile" in desc_lower or "footpath" in desc_lower:
        determined_category = "Road Damage"

    # Rule: If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW
    # In this script, if it falls through to "Other" unexpectedly, we flag it.
    flag = ""
    if determined_category == "Other" and "other" not in desc_lower:
         flag = "NEEDS_REVIEW"
         
    # Handle overlap/ambiguity checks based on specific rules (e.g. Missing Manhole -> Road Damage / Drain)
    if "drain blocked" in desc_lower:
        determined_category = "Drain Blockage"
        
    reason = "No specific reason extracted."
    if priority == "Urgent":
        # Extract the sentence containing the severity keyword
        sentences = re.split(r'(?<=[.!?]) +', description)
        for s in sentences:
            if any(kw in s.lower() for kw in SEVERITY_KEYWORDS):
                reason = f"Description contains severity keyword: {s.strip()}"
                break
    else:
        # Just grab the first sentence as a fallback reason for Standard/Low
        sentences = re.split(r'(?<=[.!?]) +', description)
        if sentences:
            reason = f"Classified based on description: {sentences[0].strip()}"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": determined_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    # Include original data plus new fields, but output requirement says:
                    # results_[city].csv should have original data plus category, priority, reason, flag
                    row.update(result)
                    results.append(row)
                except Exception as e:
                    # Skill error handling: don't crash on bad rows
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = f"Error processing row: {str(e)}"
                    row["flag"] = "NEEDS_REVIEW"
                    results.append(row)
                    
        if not results:
            print("No data found to write.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Failed to process files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
