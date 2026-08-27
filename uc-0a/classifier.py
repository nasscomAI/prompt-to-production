"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md rules.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the agents.md enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    category = "Other"
    reason = "The description did not clearly match any specific category."
    flag = "NEEDS_REVIEW"
    
    # Keyword mapping for exact category enforcement
    category_keywords = {
        "Pothole": ["pothole", "crater"],
        "Heritage Damage": ["heritage", "historic", "monument", "ancient"],
        "Drain Blockage": ["drain blocked", "drain", "clog", "sewage"],
        "Flooding": ["flood", "waterlogging", "rain"],
        "Streetlight": ["streetlight", "lights out", "dark", "sparking", "unlit", "lamp post", "substation"],
        "Waste": ["garbage", "waste", "dump", "smell", "animal", "debris", "litter"],
        "Noise": ["noise", "music", "loud", "drilling", "amplifier", "band"],
        "Heat Hazard": ["heat", "sun", "stroke", "temperature", "melting", "44°c", "45°c", "52°c"],
        "Road Damage": ["road surface", "cracked", "manhole", "tiles broken", "footpath", "bridge", "subside", "buckled", "paving", "cobblestone"]
    }
    
    matched_word = ""
    for cat, kws in category_keywords.items():
        for kw in kws:
            if kw in desc:
                category = cat
                matched_word = kw
                flag = ""
                break
        if category != "Other":
            break
            
    # Priority enforcement check for severity keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    sev_word = ""
    
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            sev_word = kw
            break
            
    # Reason construction citing specific words from the description
    if category != "Other":
        if priority == "Urgent":
            reason = f"Classified as {category} with Urgent priority because description mentions '{matched_word}' and '{sev_word}'."
        else:
            reason = f"Classified as {category} because description mentions '{matched_word}'."
            
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
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if not row or not row.get('description'):
                        # Flag nulls
                        results.append({
                            "complaint_id": row.get("complaint_id", "UNKNOWN"),
                            "category": "Other",
                            "priority": "Low",
                            "reason": "Null or empty description provided.",
                            "flag": "NEEDS_REVIEW"
                        })
                        continue
                    
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Handle bad rows without crashing
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            if not results:
                print("No results to write.")
                return
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
