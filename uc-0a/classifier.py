"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based strictly on the text description.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority check: Urgent if severity keywords present
    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    priority = "Standard"
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            break
            
    # Category mapping based on allowed exact strings
    category = "Other"
    
    if "pothole" in desc:
        category = "Pothole"
    elif "flood" in desc or "rain" in desc:
        if "drain" in desc or "blocked" in desc:
            category = "Drain Blockage"
        else:
            category = "Flooding"
    elif "streetlight" in desc or "light" in desc or "dark" in desc:
        if "heritage" in desc:
            category = "Heritage Damage"
        else:
            category = "Streetlight"
    elif "waste" in desc or "garbage" in desc or "dead animal" in desc or "dump" in desc:
        category = "Waste"
    elif "music" in desc or "noise" in desc:
        category = "Noise"
    elif "road" in desc or "crack" in desc or "manhole" in desc or "footpath" in desc:
        category = "Road Damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "heat" in desc:
        category = "Heat Hazard"
    elif "drain" in desc:
        category = "Drain Blockage"
        
    flag = ""
    # Refusal logic if genuinely ambiguous
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Category could not be determined from the description alone."
    else:
        # Provide a one-sentence reason citing specific words
        tracked_words = [
            "pothole", "flood", "rain", "drain", "blocked", "streetlight", 
            "light", "dark", "waste", "garbage", "dead animal", "dump", 
            "music", "noise", "crack", "manhole", "footpath", "heritage", "heat"
        ]
        cited = [w for w in tracked_words if w in desc]
        cite_word = cited[0] if cited else "the description"
        reason = f"Classified as {category} because the description mentions '{cite_word}'."
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, and ensure output despite failures.
    """
    with open(input_path, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
        
    for f in ["category", "priority", "reason", "flag"]:
        if f not in fieldnames:
            fieldnames.append(f)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            try:
                # Handle nulls
                if not row or not row.get("description"):
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = "Null or missing description."
                    row["flag"] = "NEEDS_REVIEW"
                else:
                    classified = classify_complaint(row)
                    row.update(classified)
            except Exception as e:
                # Fallback to prevent crash
                row["category"] = "Other"
                row["priority"] = "Low"
                row["reason"] = f"Processing error: {str(e)}"
                row["flag"] = "NEEDS_REVIEW"
                
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
