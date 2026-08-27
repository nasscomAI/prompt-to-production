"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Keyword detection for priority
    has_severity = False
    found_severity_keyword = None
    # We strip punctuation and check word boundaries
    words = re.findall(r'\b\w+\b', desc)
    for word in words:
        if word in SEVERITY_KEYWORDS:
            has_severity = True
            found_severity_keyword = word
            break
            
    priority = "Urgent" if has_severity else "Standard"

    # Category matching logic
    category = "Other"
    reason = "Could not definitively determine the category from the description alone."
    flag = "NEEDS_REVIEW"

    # Precise heuristics based on the problem descriptions and categories
    if "pothole" in desc or "crater" in desc:
        if "crater" in desc and "collapsed" in desc:
            category = "Road Damage"
            reason = f"The description explicitly mentions 'collapsed' indicating severe road damage."
            flag = ""
        else:
            category = "Pothole"
            kw = "pothole" if "pothole" in desc else "crater"
            reason = f"The description explicitly mentions '{kw}' indicating pothole issues."
            flag = ""
    elif "flood" in desc or "water" in desc:
        # Check if it's primarily a drain blockage
        if "drain" in desc and ("block" in desc or "choke" in desc):
            category = "Drain Blockage"
            reason = f"The description explicitly mentions 'drain' and 'block' indicating a blockage."
            flag = ""
        else:
            category = "Flooding"
            reason = f"The description explicitly mentions 'flood' indicating flooding."
            flag = ""
    elif "drain" in desc:
        if "block" in desc:
            category = "Drain Blockage"
            reason = f"The description explicitly mentions 'drain' and 'block'."
            flag = ""
        elif "flooded" in desc:
             category = "Flooding"
             reason = "The description mentions 'flooded', though drain was cited."
             flag = ""
        else:
            category = "Drain Blockage"
            reason = "The description cites 'drain' issues."
            flag = ""
    elif "construction drilling" in desc or "engines on" in desc or "trucks idling" in desc or "noise" in desc:
        category = "Noise"
        reason = "The description implies significant 'noise' from drilling or engines."
        flag = ""
    elif "waste" in desc or "garbage" in desc:
        category = "Waste"
        reason = f"The description explicitly mentions 'waste' or 'garbage'."
        flag = ""
        # Exception if heritage damage specifically?
        if "heritage" in desc:
            # Let's say Waste if it's just garbage overflow near heritage
            pass
    elif "heritage" in desc:
        category = "Heritage Damage"
        reason = f"The description explicitly mentions 'heritage' related damage."
        flag = ""
    elif "road collapsed" in desc:
        category = "Road Damage"
        reason = "The description mentions 'road collapsed'."
        flag = ""
    
    # Fallback reason if it's "Other"
    if category == "Other":
        reason = "Category could not be purely assigned to an allowed value based on description."

    
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
    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for i, row in enumerate(reader):
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                # Handle error per row without crashing
                results.append({
                    "complaint_id": row.get("complaint_id", f"UNKNOWN_{i}"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"System error parsing row: {e}",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
