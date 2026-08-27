import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the strict rules defined in agents.md.
    """
    description = row.get("description", "").lower()
    
    # Exact categories from enforcement rules
    cat_keywords = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlog"],
        "Streetlight": ["streetlight", "lights out", "light ", "dark"],
        "Waste": ["garbage", "waste", "trash", "dump"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["crack", "road surface", "broken", "sinking", "footpath"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat", "sunstroke", "temperature"],
        "Drain Blockage": ["drain", "manhole", "sewage"],
    }
    
    matched_cats = []
    
    for cat, kws in cat_keywords.items():
        if any(kw in description for kw in kws):
            matched_cats.append(cat)
            
    # "If the category is genuinely ambiguous, set flag to NEEDS_REVIEW and category to Other"
    flag = ""
    category = "Other"
    
    if len(matched_cats) == 1:
        category = matched_cats[0]
    elif len(matched_cats) > 1:
        flag = "NEEDS_REVIEW"
        category = "Other"
    else:
        # 0 matches
        flag = "NEEDS_REVIEW"
        category = "Other"
        
    # Priority
    # "Priority must be Urgent if description contains one of the following severity keywords..."
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    priority = "Standard"
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            break
            
    # Reason
    # "Reason must be exactly one sentence and must cite specific words from the complaint description"
    reason = "Classification assigned based on complaint description."
    words_cited = []
    
    all_kws = severity_keywords + [kw for kws in cat_keywords.values() for kw in kws]
    for kw in all_kws:
        if kw in description:
            words_cited.append(kw.strip())
            
    if words_cited:
        cited = ", ".join(sorted(set(words_cited)))
        reason = f"The description contains specific keywords such as '{cited}'."
    elif flag == "NEEDS_REVIEW":
        reason = "The description does not contain conclusive keywords to cleanly categorize the complaint."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV row by row, apply classify_complaint to each, and write out results.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Could not find {input_path}")
        sys.exit(1)
        
    results = []
    for row in rows:
        try:
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
            continue
            
    if not results:
        print("No valid rows processed.")
        return
        
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    with open(output_path, mode='w', encoding='utf-8', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
