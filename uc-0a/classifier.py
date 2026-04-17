import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # Priority enforcement logic based on severe keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"  # Default priority
    found_severity = None
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            found_severity = kw
            break
            
    # Category and validation enforcement logic
    category = "Other"
    flag = "NEEDS_REVIEW"
    citation = "none"
    
    if "pothole" in desc_lower:
        category = "Pothole"
        flag = ""
        citation = "pothole"
    elif "flood" in desc_lower or "water" in desc_lower or "knee-deep" in desc_lower:
        category = "Flooding"
        flag = ""
        citation = "flood" if "flood" in desc_lower else ("knee-deep" if "knee-deep" in desc_lower else "water")
        if "drain" in desc_lower:
            category = "Drain Blockage"
            citation = "drain"
    elif "streetlight" in desc_lower or "light" in desc_lower or "dark" in desc_lower or "electrical" in desc_lower:
        category = "Streetlight"
        flag = ""
        citation = "light" if "light" in desc_lower else ("dark" if "dark" in desc_lower else "electrical")
    elif "waste" in desc_lower or "garbage" in desc_lower or "smell" in desc_lower or "dump" in desc_lower or "animal" in desc_lower:
        category = "Waste"
        flag = ""
        citation = "garbage" if "garbage" in desc_lower else ("waste" if "waste" in desc_lower else "smell")
    elif "noise" in desc_lower or "music" in desc_lower:
        category = "Noise"
        flag = ""
        citation = "noise" if "noise" in desc_lower else "music"
    elif "crack" in desc_lower or "missing" in desc_lower or "footpath" in desc_lower or "sinking" in desc_lower or "road surface" in desc_lower:
        category = "Road Damage"
        flag = ""
        citation = "crack" if "crack" in desc_lower else ("missing" if "missing" in desc_lower else "footpath")
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
        flag = ""
        citation = "heritage"
    elif "heat" in desc_lower:
        category = "Heat Hazard"
        flag = ""
        citation = "heat"
        
    # Reason enforcement: Exactly one sentence, citing specific words
    if flag == "NEEDS_REVIEW":
        reason = "The description lacks explicit taxonomy keywords, making standard classification ambiguous without review."
    elif priority == "Urgent":
        reason = f"The description contains '{citation}' for categorisation and '{found_severity}' triggering an Urgent priority."
    else:
        reason = f"The description contains '{citation}' which maps to the category, and defaults to Standard priority."
        
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
    """
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            
            rows_to_write = []
            for row in reader:
                if not row or "complaint_id" not in row:
                    continue
                try:
                    classified = classify_complaint(row)
                    rows_to_write.append(classified)
                except Exception as e:
                    # Continue without crashing on malformed rows
                    print(f"Skipping malformed row: {row.get('complaint_id', 'unknown')}. Error: {e}")
                    
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
    except FileNotFoundError:
        print(f"Error: Could not find input file at '{input_path}'.")
    except Exception as e:
        print(f"Error during batch classification: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
