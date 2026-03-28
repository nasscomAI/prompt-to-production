"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    complaint_id = row.get("complaint_id", "")
    
    # 🚨 Priority Escalation (RICE enforcement)
    priority_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    triggered_priority_keyword = None
    for kw in priority_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            triggered_priority_keyword = kw
            break
            
    # 🏷️ Category Taxonomy (RICE enforcement)
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water", "overflow"],
        "Streetlight": ["streetlight", "light", "dark", "sparking"],
        "Waste": ["garbage", "waste", "trash", "bins", "dumped", "dead animal"],
        "Noise": ["music", "noise", "loud"],
        "Road Damage": ["crack", "sink", "footpath", "tiles"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain", "manhole", "sewage", "blockage"]
    }
    
    category = "Other"
    found_keywords = []
    
    for cat, kws in category_map.items():
        found = [kw for kw in kws if kw in desc_lower]
        if found:
            category = cat
            found_keywords = found
            break
            
    # 🚩 Flag and Reason Justification (RICE enforcement)
    flag = ""
    if category == "Other" or not description:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Category is genuinely ambiguous or input is empty, requiring manual review."
    else:
        # Citing specific words as required by enforcement rules
        citation = ", ".join(found_keywords)
        reason = f"Classified as {category} based on specific description content: '{citation}'."
        
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
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                print(f"Error: No columns found in {input_path}")
                return
            
            results = []
            for row in reader:
                results.append(classify_complaint(row))
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Fatal Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
