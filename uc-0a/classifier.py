"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    
    # Error handling: malformed or description too short
    if not isinstance(desc, str) or len(desc.strip()) < 10:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is too short or malformed.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = desc.lower()
    
    # Priority Rule: Urgent if severity keywords present
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    reason_word = None
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            reason_word = kw
            break
            
    # Category Rule: Must match strict predefined taxonomy
    category = "Other"
    flag = "NEEDS_REVIEW"
    
    categories_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water", "rain", "flooded"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["garbage", "waste", "smell", "dead animal", "dumped"],
        "Noise": ["noise", "music", "loud", "midnight"],
        "Road Damage": ["road surface", "cracked", "sinking", "footpath tiles broken", "tiles broken"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain blocked", "manhole"]
    }
    
    for cat, kws in categories_map.items():
        for kw in kws:
            if kw in desc_lower:
                category = cat
                flag = ""  # Not ambiguous anymore
                if not reason_word:
                    reason_word = kw
                break
        if category != "Other":
            break
            
    if not reason_word:
        reason_word = "unspecified issue"
        
    reason = f"The description contains '{reason_word}'."
    
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
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return
        
    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip empty rows or rows that have no meaningful data
            if not row or not any(str(v).strip() for v in row.values()):
                continue
                
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv or directory")
    parser.add_argument("--output", required=True, help="Path to write results CSV or output directory")
    args = parser.parse_args()
    
    if os.path.isdir(args.input):
        os.makedirs(args.output, exist_ok=True)
        for filename in os.listdir(args.input):
            if filename.endswith(".csv"):
                in_path = os.path.join(args.input, filename)
                out_name = filename.replace("test_", "results_")
                if not out_name.startswith("results_"):
                    out_name = "results_" + filename
                out_path = os.path.join(args.output, out_name)
                batch_classify(in_path, out_path)
                print(f"Processed {filename} -> {out_name}")
    else:
        batch_classify(args.input, args.output)
        print(f"Done. Results written to {args.output}")