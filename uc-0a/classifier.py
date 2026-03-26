"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAPPING = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "flooded", "water", "submerged", "stranded"],
    "Streetlight": ["streetlight", "light", "dark", "sparking", "unlit"],
    "Waste": ["garbage", "waste", "dump", "smell", "bin", "dead animal"],
    "Noise": ["noise", "loud", "music", "sound"],
    "Road Damage": ["road", "crack", "surface", "sinking", "manhole", "footpath", "tiles", "broken"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "temperature", "hot", "sun"],
    "Drain Blockage": ["drain", "blocked", "clog", "sewage", "overflowing"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority
    priority = "Standard"
    found_severity_kws = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            found_severity_kws.append(kw)
            
    # Category
    matched_cats = []
    found_cat_kws = []
    for cat, kws in CATEGORY_MAPPING.items():
        for kw in kws:
            if kw in desc:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                found_cat_kws.append(kw)
    
    # Ambiguity (Flagging)
    flag = ""
    if len(matched_cats) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched_cats) > 1:
        category = matched_cats[0]
        flag = "NEEDS_REVIEW"
    else:
        category = matched_cats[0]

    # Enforcement check
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Reason (One Sentence)
    if found_cat_kws and found_severity_kws:
        reason = f"The description mentions '{found_cat_kws[0]}', indicating a {category} issue, and '{found_severity_kws[0]}', resulting in an Urgent priority."
    elif found_cat_kws:
        reason = f"The description mentions '{found_cat_kws[0]}', resulting in classification as {category}."
    elif found_severity_kws:
        reason = f"The description lacks a clear category but mentions '{found_severity_kws[0]}', signaling an Urgent priority."
    else:
        reason = "No known category or severity keywords were detected."

    result = row.copy()
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            
            for new_field in ["category", "priority", "reason", "flag"]:
                if new_field not in fieldnames:
                    fieldnames.append(new_field)
            
            for row in reader:
                try:
                    results.append(classify_complaint(row))
                except Exception as e:
                    print(f"Warning: Processing row failed: {e}")
                    for nf in ["category", "priority", "reason", "flag"]:
                        if nf not in row:
                            row[nf] = ""
                    results.append(row)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
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
