"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on agents.md rules.
    """
    complaint_id = row.get("complaint_id", "")
    description = str(row.get("description", ""))
    
    if not complaint_id:
        complaint_id = "UNKNOWN_" + str(hash(description))
        
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty or missing",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Priority check -> Urgent if severity keywords present
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    urgent_keywords_found = [kw for kw in severity_keywords if kw in desc_lower]
    priority = "Urgent" if urgent_keywords_found else "Standard"
    
    # Category check
    cat_matches = []
    if "pothole" in desc_lower: cat_matches.append("Pothole")
    if "flood" in desc_lower: cat_matches.append("Flooding")
    if "streetlight" in desc_lower or ("light" in desc_lower and "dark" in desc_lower): cat_matches.append("Streetlight")
    if "waste" in desc_lower or "garbage" in desc_lower or "dump" in desc_lower or "dead animal" in desc_lower: cat_matches.append("Waste")
    if "noise" in desc_lower or "music" in desc_lower: cat_matches.append("Noise")
    if "crack" in desc_lower or "sink" in desc_lower or "surface" in desc_lower or "footpath" in desc_lower: cat_matches.append("Road Damage")
    if "heritage" in desc_lower: cat_matches.append("Heritage Damage")
    if "heat" in desc_lower: cat_matches.append("Heat Hazard")
    if "drain" in desc_lower or "manhole" in desc_lower: cat_matches.append("Drain Blockage")
    
    # Resolve ambiguity
    if "flood" in desc_lower and "drain" in desc_lower:
        cat_matches = ["Flooding", "Drain Blockage"]
    if "heritage" in desc_lower and "light" in desc_lower:
        cat_matches = ["Heritage Damage", "Streetlight"]

    # Deduplicate matches
    cat_matches = list(set(cat_matches))

    if len(cat_matches) == 1:
        category = cat_matches[0]
        flag = ""
    else:
        # Ambiguous or no matches
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Reason generation
    reason_words = []
    if urgent_keywords_found:
        reason_words.extend(urgent_keywords_found)
        
    keyword_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "garbage", "dump", "dead animal"],
        "Noise": ["noise", "music"],
        "Road Damage": ["crack", "sink", "surface", "footpath", "road"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain", "manhole"]
    }
    
    for c in cat_matches:
        for w in keyword_map.get(c, []):
            if w in desc_lower:
                reason_words.append(w)
                
    if reason_words:
        reason_str = ", ".join(list(set(reason_words)))
        reason = f"The description contains '{reason_str}'."
    else:
        reason = "Could not identify specific keywords."

    if category == "Other" and flag == "NEEDS_REVIEW":
        if cat_matches:
            reason = f"Description mentions multiple possible issues: {', '.join(cat_matches)} causing ambiguity."

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
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Row failed to process: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return
        
    if not results:
        # Write headers only
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["complaint_id", "category", "priority", "reason", "flag"])
        return
        
    with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
