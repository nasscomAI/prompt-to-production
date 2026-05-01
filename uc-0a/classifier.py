"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = str(row.get('description', '')).lower()
    
    # Allowed categories
    category = "Other"
    reason_word = "unknown issue"
    
    if "pothole" in description:
        category, reason_word = "Pothole", "pothole"
    elif "flood" in description or "water" in description:
        category, reason_word = "Flooding", "flood/water"
    elif "light" in description or "unlit" in description or "wiring" in description:
        category, reason_word = "Streetlight", "unlit/wiring"
    elif "waste" in description or "garbage" in description or "bin" in description:
        category, reason_word = "Waste", "waste/bin"
    elif "noise" in description or "loud" in description or "music" in description:
        category, reason_word = "Noise", "noise/music"
    elif "subsidence" in description or ("road" in description and "surface" in description):
        category, reason_word = "Road Damage", "subsidence/surface"
    elif "heritage" in description or "ancient" in description or "monument" in description:
        category, reason_word = "Heritage Damage", "heritage/ancient"
    elif "heat" in description or "temperature" in description or "melting" in description or "sun" in description:
        category, reason_word = "Heat Hazard", "heat/temperature"
    elif "drain" in description or "blockage" in description:
        category, reason_word = "Drain Blockage", "drain/blockage"
        
    # Priority mapping
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_keywords = [kw for kw in severity_keywords if kw in description]
    
    if found_keywords:
        priority = "Urgent"
        reason = f"Classified as {category} and marked Urgent because it mentions '{found_keywords[0]}'."
    else:
        priority = "Standard"
        reason = f"Classified as {category} because it mentions '{reason_word}'."
        
    # Flag ambiguous cases
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    return {
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
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            fieldnames = reader.fieldnames if reader.fieldnames else []
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return
        
    for new_col in ['category', 'priority', 'reason', 'flag']:
        if new_col not in fieldnames:
            fieldnames.append(new_col)
            
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in rows:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                except Exception as e:
                    row.update({
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                writer.writerow(row)
    except Exception as e:
        print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
