"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Priority Enforcement
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_severity = [kw for kw in severity_keywords if kw in description]
    priority = "Urgent" if found_severity else "Standard"
    
    # Category Enforcement
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood"],
        "Streetlight": ["streetlight", "lights out", "dark"],
        "Waste": ["garbage", "waste", "dead animal", "dumped"],
        "Noise": ["music", "noise"],
        "Road Damage": ["crack", "sinking", "footpath", "manhole"],
        "Heritage Damage": ["heritage damage"],
        "Drain Blockage": ["drain block"],
        "Heat Hazard": ["heat hazard"]
    }
    
    found_categories = []
    category_triggers = []
    for cat, kws in category_map.items():
        for kw in kws:
            if kw in description:
                if cat not in found_categories:
                    found_categories.append(cat)
                    category_triggers.append(kw)
    
    if len(found_categories) == 1:
        category = found_categories[0]
        flag = ""
        reason = f"Classified as {category} based on '{category_triggers[0]}'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Description is ambiguous, missing, or matches multiple categories."
        
    if priority == "Urgent":
        reason += f" Priority is Urgent due to severity keyword '{found_severity[0]}'."
        
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
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            
            results = []
            for row in reader:
                try:
                    # Skip completely empty rows
                    if not row or all(v is None or str(v).strip() == '' for v in row.values()):
                        continue
                        
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Do not crash on bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
