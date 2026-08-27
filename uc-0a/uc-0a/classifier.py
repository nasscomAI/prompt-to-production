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

def determine_category(description: str) -> str:
    desc_lower = description.lower()
    if "pothole" in desc_lower:
        return "Pothole"
    elif "flood" in desc_lower:
        return "Flooding"
    elif "streetlight" in desc_lower or "lights out" in desc_lower or "dark" in desc_lower:
        return "Streetlight"
    elif "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower:
        return "Waste"
    elif "music" in desc_lower or "noise" in desc_lower:
        return "Noise"
    elif "road surface cracked" in desc_lower or "manhole" in desc_lower or "footpath" in desc_lower:
        return "Road Damage"
    elif "drain blocked" in desc_lower:
        return "Drain Blockage"
    elif "heritage" in desc_lower and "damage" in desc_lower:
        return "Heritage Damage"
    elif "heat" in desc_lower:
        return "Heat Hazard"
    return "Other"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    category = determine_category(description)
    
    found_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if found_keywords:
        priority = "Urgent"
        reason = f"Classified as Urgent because it mentions '{found_keywords[0]}'."
    else:
        priority = "Standard"
        words = description.split()
        sample_words = " ".join(words[:4]) if words else "Unknown"
        reason = f"Classified based on description mentioning '{sample_words}' without severity keywords."
        
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
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
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = reader.fieldnames if reader.fieldnames else []
        
    output_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
    
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()
        
        for row in rows:
            try:
                classification = classify_complaint(row)
                row["category"] = classification.get("category", "")
                row["priority"] = classification.get("priority", "")
                row["reason"] = classification.get("reason", "")
                row["flag"] = classification.get("flag", "")
            except Exception as e:
                row["category"] = "Other"
                row["priority"] = "Standard"
                row["reason"] = f"Error during processing: {str(e)}"
                row["flag"] = "NEEDS_REVIEW"
                
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
