import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get('description', '')).lower()
    
    category = "Other"
    priority = "Standard"
    flag = ""
    reason = "Standard issue."
    
    # Keyword Categorization
    if "pothole" in desc:
        category = "Pothole"
        reason = "Description mentions 'pothole'."
    elif "flood" in desc or "water" in desc or "rain" in desc:
        category = "Flooding"
        reason = "Description references 'flood', 'water', or 'rain'."
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
        reason = "Description notes 'light' or 'dark'."
    elif "garbage" in desc or "waste" in desc or "smell" in desc:
        category = "Waste"
        reason = "Description mentions 'garbage', 'waste', or 'smell'."
    elif "music" in desc or "noise" in desc:
        category = "Noise"
        reason = "Description cites 'music' or 'noise'."
    elif "road" in desc and "crack" in desc:
        category = "Road Damage"
        reason = "Description details a 'cracked' 'road'."
    elif "heritage" in desc:
        category = "Heritage Damage"
        reason = "Description references 'heritage'."
    elif "drain" in desc or "block" in desc:
        category = "Drain Blockage"
        reason = "Description mentions 'drain' or 'blocked'."
    elif "heat" in desc:
        category = "Heat Hazard"
        reason = "Description discusses 'heat'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No clear category keywords found."

    # Urgent Priority Rules
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    for word in urgent_keywords:
        if word in desc:
            priority = "Urgent"
            reason = f"{reason} Flagged Urgent because it mentions '{word}'."
            break
            
    # Ambiguity check fallback
    if category == "Other" and flag == "":
        flag = "NEEDS_REVIEW"
        reason = "Genuinely ambiguous complaint lacking distinct keywords."

    return {
        "complaint_id": row.get("complaint_id", "Unknown"),
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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "Unknown"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
        return
        
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
    print(f"Done. Results written to {args.output}")
