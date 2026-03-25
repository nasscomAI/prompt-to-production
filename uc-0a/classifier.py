import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")
    
    # Priority Logic (Urgent if specific hazard keywords found)
    urgent_keywords = ["injury", "accident", "school", "hospital", "hazard", "emergency", "child"]
    found_urgent = [kw for kw in urgent_keywords if kw in desc]
    priority = "Urgent" if found_urgent else "Normal"
    
    # Category Logic (Must map to one of the defined list)
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "rain": "Flooding",
        "water": "Flooding",
        "light": "Streetlight",
        "dark": "Streetlight",
        "garbage": "Garbage",
        "waste": "Garbage",
        "smell": "Garbage",
        "leak": "Water Leakage",
        "noise": "Noise",
        "music": "Noise",
        "crack": "Other",
        "animal": "Garbage",
        "tiles": "Other"
    }
    
    assigned_category = "Other"
    flag = "NEEDS_REVIEW"
    cat_kw = ""
    
    for kw, cat in category_map.items():
        if kw in desc:
            assigned_category = cat
            if cat != "Other":
                flag = ""  # Clear flag if we have a confident category
            cat_kw = kw
            break
            
    # Reason Logic (Must cite specific keywords)
    reason_parts = []
    if assigned_category == "Other":
        reason_parts.append("flag set to NEEDS_REVIEW due to ambiguity")
    else:
        reason_parts.append(f"category keyword '{cat_kw}'")
        
    if found_urgent:
        reason_parts.append(f"urgent keyword(s) '{', '.join(found_urgent)}'")
        
    reason = f"Classified based on description containing: {'; '.join(reason_parts)}"

    return {
        "complaint_id": complaint_id,
        "category": assigned_category,
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
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Provide default for completely empty rows
                    if not row:
                        raise ValueError("Empty row")
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN",
                        "category": "Other",
                        "priority": "Normal",
                        "reason": f"Error classifying row: {str(e)}. Flagged for review.",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Fatal error processing batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
