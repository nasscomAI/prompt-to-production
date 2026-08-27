import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    comp_id = row.get('complaint_id', 'UNKNOWN')
    desc = row.get('description', '').lower()
    
    if not desc:
        return {
            "complaint_id": comp_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description.",
            "flag": "NEEDS_REVIEW"
        }
        
    category = "Other"
    priority = "Standard"
    flag = ""
    reason = ""
    
    # Category Assignment via Keyword Mapping
    if "pothole" in desc:
        category = "Pothole"
        reason = "Description mentions 'pothole'."
    elif "drain" in desc and "blocked" in desc:
        category = "Drain Blockage"
        reason = "Description mentions 'drain' and 'blocked'."
    elif "drain" in desc or "mosquito breeding" in desc:
        category = "Drain Blockage"
        reason = "Description mentions 'drain' or 'mosquito'."
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
        reason = "Description mentions 'flood' or 'water'."
    elif "waste" in desc or "garbage" in desc or "debris" in desc:
        category = "Waste"
        reason = "Description mentions 'waste', 'garbage' or 'debris'."
    elif "noise" in desc or "drilling" in desc or "idling" in desc or "engines" in desc:
        category = "Noise"
        reason = "Description mentions noise factors intentionally ('drilling', 'engines', etc)."
    elif "road collapsed" in desc or "crater" in desc:
        category = "Road Damage"
        reason = "Description mentions 'crater' or 'road collapsed'."
    elif "heritage" in desc:
        category = "Heritage Damage"
        reason = "Description mentions 'heritage'."
    elif "heat" in desc:
        category = "Heat Hazard"
        reason = "Description mentions 'heat'."
    elif "light" in desc:
        category = "Streetlight"
        reason = "Description mentions 'light'."
    else:
        # Ambiguous
        category = "Other"
        reason = "No definitive category keywords found."
        flag = "NEEDS_REVIEW"

    # Multi-category ambiguity overrides
    if "heritage" in desc and "garbage" in desc:
        # e.g., "Heritage zone garbage overflow"
        category = "Waste"
        reason += " Categorised as Waste due to 'garbage'."
        
    if "drain" in desc and "flood" in desc:
        category = "Drain Blockage"
        reason = "Drain blockage takes precedence over generic flooding."

    # Severity Check
    found_severe = [kw for kw in URGENT_KEYWORDS if kw in desc]
    if found_severe:
        priority = "Urgent"
        reason += f" Escalated to Urgent due to keyword '{found_severe[0]}'."
    else:
        if category in ["Other", "Noise", "Waste"]:
            priority = "Low"
        else:
            priority = "Standard"

    return {
        "complaint_id": comp_id,
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row linearly, write results CSV.
    """
    results = []
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error handling row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read input file {input_path}. Error: {str(e)}")
        return

    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output file {output_path}. Error: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
