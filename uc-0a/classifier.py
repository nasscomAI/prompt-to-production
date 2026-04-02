import argparse
import csv
import sys
import re

# Enforced constraints from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to the rules defined in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()
    
    # 1. Determine Category ensuring strict adherence to allowed list (No Hallucinated sub-categories)
    category = "Other"
    
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "drain block" in desc_lower:
        category = "Drain Blockage"
    elif "flood" in desc_lower or "rain" in desc_lower:
        category = "Flooding"
    elif "light" in desc_lower:
        category = "Streetlight"
    elif "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower or "dumped" in desc_lower:
        category = "Waste"
    elif "music" in desc_lower or "noise" in desc_lower:
        category = "Noise"
    elif "crack" in desc_lower or "tiles broken" in desc_lower or "manhole" in desc_lower:
        category = "Road Damage"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
    elif "heat" in desc_lower:
        category = "Heat Hazard"
        
    # 2. Assign Needs Review Flag for Ambiguity
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # 3. Determine Priority (Mitigating Severity blindness)
    priority = "Standard"
    matched_keywords = [kw for kw in SEVERITY_KEYWORDS if re.search(rf'\b{kw}\b', desc_lower)]
    
    if matched_keywords:
        priority = "Urgent"
        
    # 4. Extract Justification Reason (Exactly one sentence citing specific words)
    if matched_keywords:
        reason = f"Assigned '{category}' category and 'Urgent' priority because the description explicitly mentions the severity keyword '{matched_keywords[0]}'."
    else:
        # Provide reason based on matched tokens, fallback if empty
        words = desc.split()
        snippet = " ".join(words[:4]) + "..." if words else "an empty description"
        reason = f"Assigned '{category}' category and 'Standard' priority based on the context starting with '{snippet}'."
        
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row using skills.md logic, write results CSV.
    Must not crash on bad rows.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Error handling defined in skills.md
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification failed due to internal error.",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)

    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Classified results confidently compiled in {args.output}.")
