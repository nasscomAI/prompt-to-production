"""
UC-0A — Complaint Classifier
Built based on the RICE framework, agents.md and skills.md.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower() if row.get("description") else ""
    
    # 1. Enforcement: Priority Severity keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    reason_priority_word = None
    
    for kw in urgent_keywords:
        if kw in desc:
            priority = "Urgent"
            reason_priority_word = kw
            break
            
    # 2. Enforcement: Exact Category List
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "spark": "Streetlight",
        "light": "Streetlight",
        "dark": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "dead animal": "Waste",
        "smell": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "crack": "Road Damage",
        "broken": "Road Damage",
        "sink": "Road Damage",
        "footpath": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "manhole": "Road Damage" # Categorizing manhole issues as Road Damage based on descriptions
    }
    
    category = "Other"
    flag = "NEEDS_REVIEW"
    cat_word = None
    
    # Find matching category keyword
    for kw, cat in category_map.items():
        if kw in desc:
            category = cat
            flag = ""
            cat_word = kw
            break
            
    # 3. Enforcement: Exact sentence reason citing words
    if category == "Other":
        reason = "Could not confidently determine category from the description."
        flag = "NEEDS_REVIEW"
    else:
        if priority == "Urgent":
            reason = f"Classified as {category} with Urgent priority due to presence of '{cat_word}' and '{reason_priority_word}'."
        else:
            reason = f"Classified as {category} based on the word '{cat_word}'."
            
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
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Empty input file or bad headers.")
                return
            
            # Ensure our newly generated fields are in the output headers
            output_fields = list(fieldnames)
            for f in ["category", "priority", "reason", "flag"]:
                if f not in output_fields:
                    output_fields.append(f)
                    
            rows_to_write = []
            
            for row in reader:
                try:
                    result = classify_complaint(row)
                    # Update row with results
                    for k in ["category", "priority", "reason", "flag"]:
                        row[k] = result.get(k, "")
                    rows_to_write.append(row)
                except Exception as e:
                    # Error handling: Flags bad rows and produces output anyway
                    row['category'] = "Other"
                    row['priority'] = "Standard"
                    row['reason'] = f"Error processing row: {str(e)}"
                    row['flag'] = "NEEDS_REVIEW"
                    rows_to_write.append(row)
                    
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
    except Exception as e:
        print(f"Failed to process batch classification: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
