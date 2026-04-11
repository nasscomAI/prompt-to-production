"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Check severity keywords for Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    matched_urgent_word = None
    
    for kw in urgent_keywords:
        if kw in desc:
            priority = "Urgent"
            matched_urgent_word = kw
            break
            
    # Check category mappings
    cat_hints = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "dead animal": "Waste",
        "noise": "Noise",
        "music": "Noise",
        "road surface": "Road Damage",
        "manhole cover": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain block": "Drain Blockage"
    }
    
    matched_cats = set()
    first_cat_kw = None
    
    for k, v in cat_hints.items():
        if k in desc:
            matched_cats.add(v)
            if not first_cat_kw:
                first_cat_kw = k
                
    # Evaluate ambiguity and determine category
    if len(matched_cats) == 1:
        category = list(matched_cats)[0]
        flag = ""
    else:
        # Multiple matched categories or none matched -> Ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Construct exact-sentence reason
    reason_word = matched_urgent_word if matched_urgent_word else first_cat_kw if first_cat_kw else "unclear text"
    reason = f"Classified based on the specific word '{reason_word}' extracted from the description."
    
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
    Safely processing without crashing on bad rows.
    """
    processed_rows = []
    field_names = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            field_names = reader.fieldnames if reader.fieldnames else []
            for row in reader:
                try:
                    result = classify_complaint(row)
                    row.update(result)
                    processed_rows.append(row)
                except Exception as e:
                    print(f"Skipping/flagging row due to error: {e}")
                    row.update({"category": "Other", "priority": "Low", "reason": f"Error: {e}", "flag": "NEEDS_REVIEW"})
                    processed_rows.append(row)
    except Exception as e:
        print(f"Failed opening input file: {e}")
        return

    if not processed_rows:
        print("No valid rows to write.")
        return

    # Add our new columns
    out_fields = field_names.copy()
    for new_col in ["category", "priority", "reason", "flag"]:
        if new_col not in out_fields:
            out_fields.append(new_col)
            
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fields)
            writer.writeheader()
            for row in processed_rows:
                writer.writerow(row)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
