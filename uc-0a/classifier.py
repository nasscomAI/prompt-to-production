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
    
    # Determine priority based on severity keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    cited_word = ""
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            cited_word = kw
            break
            
    # Determine category based on keywords
    matches = []
    if "pothole" in desc or "surface cracked" in desc:
        matches.append(("Pothole", "pothole" if "pothole" in desc else "surface cracked"))
    if "flood" in desc or "water" in desc:
        matches.append(("Flooding", "flood" if "flood" in desc else "water"))
    if "streetlight" in desc or "lights out" in desc or "dark" in desc or "sparking" in desc:
        matches.append(("Streetlight", "streetlight" if "streetlight" in desc else "lights out" if "lights out" in desc else "sparking" if "sparking" in desc else "dark"))
    if "garbage" in desc or "waste" in desc or "dead animal" in desc or "smell" in desc:
        matches.append(("Waste", "garbage" if "garbage" in desc else "dead animal" if "dead animal" in desc else "waste" if "waste" in desc else "smell"))
    if "music" in desc or "noise" in desc:
        matches.append(("Noise", "music" if "music" in desc else "noise"))
    if "manhole" in desc or "footpath" in desc:
        matches.append(("Road Damage", "manhole" if "manhole" in desc else "footpath"))
    if "heritage" in desc:
        matches.append(("Heritage Damage", "heritage"))
    if "heat" in desc:
        matches.append(("Heat Hazard", "heat"))
    if "drain blocked" in desc or "drain" in desc:
        matches.append(("Drain Blockage", "drain blocked" if "drain blocked" in desc else "drain"))
        
    category = "Other"
    flag = ""
    
    if len(matches) == 1:
        category = matches[0][0]
        if not cited_word:
            cited_word = matches[0][1]
    elif len(matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if not cited_word:
            cited_word = matches[0][1]
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if not cited_word:
            words = desc.split()
            cited_word = words[0] if words else "issue"
            
    # Edge case observed in data: both 'flood' and 'drain blocked' means NEEDS_REVIEW as it's multiple matches.
            
    reason = f"The description contains the word '{cited_word}'."
    
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
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error parsing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error opening input file: {e}")
        return
        
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Error writing to output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
