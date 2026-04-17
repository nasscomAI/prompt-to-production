import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Priority classification
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_urgent_kw = None
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            found_urgent_kw = kw
            break
            
    # Category rules
    kw_to_cat = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "lights out": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "dead animal": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "crack": "Road Damage",
        "footpath": "Road Damage",
        "sinking": "Road Damage",
        "heritage": "Heritage Damage",
        "drain blocked": "Drain Blockage",
        "drain block": "Drain Blockage"
    }
    
    matched_categories = set()
    found_cat_kw = None
    for kw, cat in kw_to_cat.items():
        if kw in description:
            matched_categories.add(cat)
            found_cat_kw = kw
            
    # Error handling / Ambiguity
    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
        flag = ""
        if found_urgent_kw:
            reason = f"Contains '{found_cat_kw}', and marked Urgent due to '{found_urgent_kw}'."
        else:
            reason = f"Contains '{found_cat_kw}'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if found_urgent_kw:
             reason = f"Ambiguous category, but Urgent due to '{found_urgent_kw}'."
        else:
             reason = "Category cannot be clearly determined from description alone."

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
    if not os.path.exists(input_path):
        print(f"Error: Missing input file at {input_path}")
        return
        
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Basic validation: Skip completely broken/empty rows
                if not row.get("complaint_id") or not row.get("description"):
                    continue
                results.append(classify_complaint(row))
            except Exception as e:
                # Skill instruction: skip invalid rows
                pass
                
    # Ensure output directory exists before writing
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
                
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
