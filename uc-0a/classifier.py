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
    desc = row.get("description", "").lower()
    
    # Severity check
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    urgent_match = next((kw for kw in urgent_keywords if kw in desc), None)
    
    priority = "Urgent" if urgent_match else "Standard"
    
    # Category mapping heuristics
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "unlit": "Streetlight",
        "light": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "trash": "Waste",
        "noise": "Noise",
        "music": "Noise",
        "road": "Road Damage",
        "tarmac": "Road Damage",
        "surface": "Road Damage",
        "subsidence": "Road Damage",
        "heritage": "Heritage Damage",
        "ancient": "Heritage Damage",
        "heat": "Heat Hazard",
        "temperature": "Heat Hazard",
        "sun": "Heat Hazard",
        "burn": "Heat Hazard",
        "drain": "Drain Blockage"
    }
    
    matched_cat_keywords = []
    for kw, cat in category_map.items():
        if kw in desc:
            matched_cat_keywords.append((kw, cat))
    
    # Reason construction
    if urgent_match:
        reason = f"Flagged as urgent due to keyword '{urgent_match}'."
    elif matched_cat_keywords:
        reason = f"Categorized based on keyword '{matched_cat_keywords[0][0]}'."
    else:
        reason = "Could not confidently determine a specific category from description."

    # Decide final category and flag
    flag = ""
    if not matched_cat_keywords:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        # Check for ambiguity (multiple different categories matched)
        unique_matched_cats = list(set([cat for kw, cat in matched_cat_keywords]))
        if len(unique_matched_cats) > 1:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason = f"Ambiguous description matching multiple categories: {', '.join(unique_matched_cats)}"
        else:
            category = unique_matched_cats[0]

    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
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
        results = []
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Not crashing on bad rows
                    print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
        
        if not results:
            print("Warning: No results generated. Input might be empty.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
                
    except Exception as general_error:
        print(f"Critical error during batch classification: {general_error}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
