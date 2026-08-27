import argparse
import csv
import os

# Taxonomy and Rules from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords for Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based enforcement for priority
    and taxonomy mapping for categories as defined in agents.md.
    """
    description = row.get('description', '').strip()
    desc_lower = description.lower()
    complaint_id = row.get('complaint_id', 'unknown')

    # 1. Enforcement: Priority Rules
    priority = "Standard"
    if any(keyword in desc_lower for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif "urgent" in desc_lower or "immediate" in desc_lower:
        priority = "Urgent"
    else:
        # Default logic for non-urgent
        priority = "Standard"

    # 2. Enforcement: Category Classification (Taxonomy)
    category = "Other"
    flag = ""
    reason = ""

    # Mapping keywords to categories
    if "pothole" in desc_lower:
        category = "Pothole"
        reason = "The description specifically cites a 'pothole' issue."
    elif "flood" in desc_lower or ("water" in desc_lower and "drain" not in desc_lower):
        category = "Flooding"
        reason = "The text mentions 'flooding' or water-related distress."
    elif "light" in desc_lower:
        category = "Streetlight"
        reason = "The complaint identifies a 'streetlight' failure."
    elif any(kw in desc_lower for kw in ["waste", "garbage", "bin", "trash"]):
        category = "Waste"
        reason = "The presence of 'waste' or 'garbage' indicates this category."
    elif any(kw in desc_lower for kw in ["noise", "loud", "music"]):
        category = "Noise"
        reason = "The description reports a 'noise' disturbance."
    elif "road" in desc_lower and ("damage" in desc_lower or "crack" in desc_lower or "sinking" in desc_lower):
        category = "Road Damage"
        reason = "The text describes 'road damage' or surface degradation."
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
        reason = "The complaint refers to 'heritage' site concerns."
    elif "heat" in desc_lower or "temperature" in desc_lower:
        category = "Heat Hazard"
        reason = "The description highlights a 'heat hazard' condition."
    elif "drain" in desc_lower or "sewage" in desc_lower:
        category = "Drain Blockage"
        reason = "The issue involves a 'drain blockage' or sewage overflow."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "The category is ambiguous and requires manual review."

    # Final enforcement check
    if category not in ALLOWED_CATEGORIES:
        category = "Other"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results to CSV.
    Handles nulls and ensures the process doesn't crash on bad rows.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            # Handle nulls/missing descriptions
            if not row.get('description'):
                results.append({
                    "complaint_id": row.get('complaint_id', 'unknown'),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Missing or null description field.",
                    "flag": "NEEDS_REVIEW"
                })
                continue
            
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Log error and continue
                print(f"Failed to process row {row.get('complaint_id')}: {e}")
                results.append({
                    "complaint_id": row.get('complaint_id', 'unknown'),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    # Write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  default="../data/city-test-files/test_pune.csv", help="Path to test_[city].csv")
    parser.add_argument("--output", default="results_pune.csv", help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
