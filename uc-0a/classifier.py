"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", 
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_RULES = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogged"],
    "Streetlight": ["streetlight", "light out", "lights out", "dark at night", "flickering and sparking"],
    "Waste": ["garbage", "waste", "dead animal", "dumped"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["road surface cracked", "cracked and sinking", "footpath tiles broken", "road broken", "crack"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heatwave", "sunstroke", "blistering"],
    "Drain Blockage": ["drain blocked", "drain", "manhole", "sewage", "gutter"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    try:
        complaint_id = row.get("complaint_id", "UNKNOWN")
        description = row.get("description", "").strip()
        desc_lower = description.lower()
        
        if not description:
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": "Description is completely missing.",
                "flag": "NEEDS_REVIEW"
            }

        # 1. Determine Priority
        severe_matches = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
        if severe_matches:
            priority = "Urgent"
            base_reason = f"Contains severity keyword '{severe_matches[0]}'."
        else:
            priority = "Standard"
            base_reason = "No severity keywords detected."

        # 2. Determine Category
        matched_cats = []
        for cat, kws in CATEGORY_RULES.items():
            if any(kw in desc_lower for kw in kws):
                matched_cats.append(cat)
                
        if len(matched_cats) == 1:
            category = matched_cats[0]
            flag = ""
            matched_kw = next(kw for kw in CATEGORY_RULES[category] if kw in desc_lower)
            reason = f"{base_reason} Assigned '{category}' based on '{matched_kw}'."
        elif len(matched_cats) > 1:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason = f"{base_reason} Ambiguous: matches multiple categories ({', '.join(matched_cats)})."
        else:
            category = "Other"
            if priority == "Standard":
                flag = "NEEDS_REVIEW"
            else:
                flag = ""
            reason = f"{base_reason} No matched category keywords so defaulting to Other."
            
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }
    except Exception as e:
        return {
            "complaint_id": row.get("complaint_id", "UNKNOWN"),
            "category": "Other",
            "priority": "Low",
            "reason": f"Malformed row processing error: {str(e)}",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)
            
    # Ensure directory exists before opening outfile
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
