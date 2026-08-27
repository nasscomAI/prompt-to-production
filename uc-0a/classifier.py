import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Built based on requirements from agents.md and skills.md.
    """
    description = row.get("description", "").lower()
    
    # --- Priority Logic ---
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for word in urgent_keywords:
        if word in description:
            priority = "Urgent"
            break
            
    # --- Category Logic ---
    category = "Other"
    ambiguous = False
    
    # Hardcoded deterministic taxonomy matching
    taxonomy = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "lights out": "Streetlight",
        "streetlight": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "dead animal": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "crack": "Road Damage",
        "broken": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain blocked": "Drain Blockage",
        "drain": "Drain Blockage",
        "manhole cover missing": "Other"
    }

    # Extract all matching categories
    matched_cats = {}
    for kw, cat in taxonomy.items():
        if kw in description:
            if cat not in matched_cats:
                matched_cats[cat] = kw

    reason = ""
    # Map matched components to exact categories safely
    if len(matched_cats) == 0:
        category = "Other"
        ambiguous = True
        reason = "The description does not contain clear taxonomy keywords."
    elif len(matched_cats) == 1:
        category = list(matched_cats.keys())[0]
        trigger_word = list(matched_cats.values())[0]
        reason = f"The description correctly cites '{trigger_word}'."
        # Exception for missing manhole covers since "Other" isn't perfectly classified usually
        if trigger_word == "manhole cover missing":
            ambiguous = True
    else:
        # Multiple mismatches implies overlapping concerns, fulfilling the NEEDS_REVIEW intent
        category = list(matched_cats.keys())[0]
        trigger_words = list(matched_cats.values())
        reason = f"The description cites conflicting issues like '{trigger_words[0]}' and '{trigger_words[1]}'."
        ambiguous = True

    flag = "NEEDS_REVIEW" if ambiguous else ""

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
    Safely skips/recovers bad rows following the skills.md error handling.
    """
    results = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified_row = classify_complaint(row)
                results.append(classified_row)
            except Exception as e:
                # Skill constraint: Don't crash on bad rows, flag it instead
                results.append({
                    "complaint_id": row.get("complaint_id", "ERROR"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Exception encountered during classification: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    # Write classified output
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for res in results:
            writer.writerow(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
