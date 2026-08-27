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
    if not desc:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty.",
            "flag": "NEEDS_REVIEW"
        }
    
    # Priority classification
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_severity = [kw for kw in severity_keywords if kw in desc]
    priority = "Urgent" if found_severity else "Standard"
    
    # Category mapping keywords
    categories = {
        "Pothole": ["pothole"],
        "Flooding": ["flood"],
        "Streetlight": ["streetlight", "lights out", "dark"],
        "Waste": ["garbage", "waste", "dead animal"],
        "Noise": ["music", "noise"],
        "Road Damage": ["road surface", "broken", "cracked", "manhole", "tiles"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain block"]
    }
    
    matched_cats = {}
    for cat, kws in categories.items():
        for kw in kws:
            if kw in desc:
                if cat not in matched_cats:
                    matched_cats[cat] = []
                matched_cats[cat].append(kw)
    
    flag = ""
    if not matched_cats:
        category = "Other"
        reason = "No known category keywords found in the description."
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cat_reasons = [f"'{matched_cats[c][0]}' implies {c}" for c in matched_cats]
        reason = f"Genuinely ambiguous as {' and '.join(cat_reasons)}."
    else:
        category = list(matched_cats.keys())[0]
        trigger_word = matched_cats[category][0]
        reason_parts = [f"The keyword '{trigger_word}' correctly identifies this as {category}."]
        if found_severity:
            reason_parts.append(f"The severity keyword '{found_severity[0]}' escalates priority to Urgent.")
        reason = " ".join(reason_parts)
        
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
    
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return
        
    for row in rows:
        try:
            result = classify_complaint(row)
            row.update(result)
            results.append(row)
        except Exception as e:
            print(f"Warning: Failed to process row {row.get('complaint_id', 'UNKNOWN')}: {e}")
            continue
            
    if not results:
        print("No valid results generated.")
        return
        
    try:
        out_fieldnames = fieldnames.copy()
        for field in ["category", "priority", "reason", "flag"]:
            if field not in out_fieldnames:
                out_fieldnames.append(field)
                
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
