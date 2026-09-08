"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "")
    
    # Check priority based on severity keywords
    priority = "Standard"
    desc_lower = description.lower()
    for keyword in URGENT_KEYWORDS:
        if keyword in desc_lower:
            priority = "Urgent"
            break
            
    # Simple rule-based categorization matching keywords to allowed categories
    category = "Other"
    flag = ""
    
    if not description:
        flag = "NEEDS_REVIEW"
    elif "pothole" in desc_lower or "road hole" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower or "waterlogging" in desc_lower or "overflow" in desc_lower:
        category = "Flooding"
    elif "light" in desc_lower or "lamp" in desc_lower:
        category = "Streetlight"
    elif "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower:
        category = "Waste"
    elif "noise" in desc_lower or "loud" in desc_lower:
        category = "Noise"
    elif "damage" in desc_lower or "crack" in desc_lower:
        category = "Road Damage"
    elif "heritage" in desc_lower or "monument" in desc_lower:
        category = "Heritage Damage"
    elif "heat" in desc_lower or "hot" in desc_lower:
        category = "Heat Hazard"
    elif "drain" in desc_lower or "block" in desc_lower:
        category = "Drain Blockage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    reason = f"Classified as {category} based on description text."

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
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            # Ensure output schema includes our target fields
            output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
            
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception:
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Error processing row.",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
                
    except Exception as e:
        print(f"Error during batch classification: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

