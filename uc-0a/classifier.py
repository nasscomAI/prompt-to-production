"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def get_category_and_ambiguity(description: str):
    desc_lower = description.lower()
    
    if "pothole" in desc_lower:
        return "Pothole", False
    if "flood" in desc_lower:
        return "Flooding", False
    if "drain" in desc_lower and "block" in desc_lower:
        return "Drain Blockage", False
    if "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower:
        return "Waste", False
    if "music" in desc_lower or "noise" in desc_lower:
        return "Noise", False
    if "road surface" in desc_lower or "footpath" in desc_lower or "manhole" in desc_lower:
        return "Road Damage", False
    if "heritage" in desc_lower:
        return "Heritage Damage", False
    if "streetlight" in desc_lower or "lights out" in desc_lower or "dark" in desc_lower:
        return "Streetlight", False
    if "heat" in desc_lower:
        return "Heat Hazard", False
        
    return "Other", True

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()
    
    # Determine Priority
    priority = "Standard"
    found_keywords = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            found_keywords.append(kw)
            priority = "Urgent"
            
    # Determine Category
    category, is_ambiguous = get_category_and_ambiguity(desc)
    
    flag = "NEEDS_REVIEW" if is_ambiguous else ""
    
    if found_keywords:
        reason = f"Description contains severity keyword(s): {', '.join(found_keywords)}."
    else:
        reason = "No severity keywords detected; normal priority."
    
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result_row = classify_complaint(row)
                    results.append(result_row)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error parsing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_path}")
        return
        
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
    except Exception as e:
        print(f"Error writing to output file: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
