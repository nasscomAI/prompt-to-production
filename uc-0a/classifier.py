"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the description text, 
    adhering strictly to the rules defined in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # --- PRIORITY CLASSIFICATION ---
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    reason_priority_str = ""
    
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            reason_priority_str = f" severity keyword '{kw}'"
            break
            
    # --- CATEGORY CLASSIFICATION ---
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "rain", "water", "inundated"],
        "Streetlight": ["streetlight", "lights out", "dark at night", "flickering", "sparking"],
        "Waste": ["garbage", "waste", "dead animal", "smell", "dumped"],
        "Noise": ["music", "noise", "loud", "wedding"],
        "Road Damage": ["road surface cracked", "cracks", "sinking", "tiles broken", "upturned", "road"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "sun"],
        "Drain Blockage": ["drain blocked", "drain", "manhole"]
    }
    
    matched_cats = []
    matched_kws = []
    for cat, kws in category_map.items():
        for kw in kws:
            # simple keyword matching
            if kw in description:
                # specifically for 'road' keyword not overlapping 'road damage' roughly
                if kw == "road" and cat == "Road Damage" and "pothole" in description:
                    continue  # Pothole takes precedence usually over raw road damage text if pothole present
                if cat not in matched_cats:
                    matched_cats.append(cat)
                    matched_kws.append(kw)
    
    category = "Other"
    flag = ""
    reason_cat_str = "no known keywords"
    
    if "drain" in description and "flood" in description:
        matched_cats = ["Drain Blockage"]
        matched_kws = ["drain"]

    if len(matched_cats) == 1:
        category = matched_cats[0]
        reason_cat_str = f"keyword '{matched_kws[0]}'"
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cat_str = f"multiple conflicting keywords ({', '.join(matched_kws)})"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # --- REASON CONSTRUCTION ---
    if priority == "Urgent":
        reason = f"Classified as {category} due to {reason_cat_str} and marked Urgent due to{reason_priority_str}."
    else:
        reason = f"Classified as {category} due to {reason_cat_str}."
        
    if category == "Other" and flag != "NEEDS_REVIEW":
        flag = "NEEDS_REVIEW"

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
    results = []
    fieldnames = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                fieldnames = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]
            
            for row_idx, row in enumerate(reader):
                try:
                    classified = classify_complaint(row)
                    row.update(classified)
                    results.append(row)
                except Exception as e:
                    print(f"Error processing row {row_idx}: {e}")
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = f"Processing failed: {str(e)}"
                    row["flag"] = "NEEDS_REVIEW"
                    results.append(row)
                    
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return
        
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Output file error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
