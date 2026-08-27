"""
UC-0A — Complaint Classifier
Implemented using RICE constraints from agents.md and skills.md.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine Priority
    priority = "Standard"
    matched_urgent_word = None
    for kw in URGENT_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            matched_urgent_word = kw
            break
            
    # 2. Determine Category
    category_matches = []
    matched_cat_word = None
    
    if "pothole" in desc:
        category_matches.append("Pothole")
        matched_cat_word = "pothole"
    if "flood" in desc or "water" in desc:
        category_matches.append("Flooding")
        if not matched_cat_word: matched_cat_word = "flood/water"
    if "streetlight" in desc or "lights out" in desc or "dark" in desc:
        category_matches.append("Streetlight")
        if not matched_cat_word: matched_cat_word = "streetlight/dark"
    if "garbage" in desc or "waste" in desc or "dead animal" in desc:
        category_matches.append("Waste")
        if not matched_cat_word: matched_cat_word = "garbage/waste"
    if "noise" in desc or "music" in desc:
        category_matches.append("Noise")
        if not matched_cat_word: matched_cat_word = "music/noise"
    if "crack" in desc or "tiles broken" in desc or "sinking" in desc:
        category_matches.append("Road Damage")
        if not matched_cat_word: matched_cat_word = "crack/broken"
    if "heritage" in desc:
        category_matches.append("Heritage Damage")
        if not matched_cat_word: matched_cat_word = "heritage"
    if "heat" in desc:
        category_matches.append("Heat Hazard")
        if not matched_cat_word: matched_cat_word = "heat"
    if "drain" in desc or "manhole" in desc:
        category_matches.append("Drain Blockage")
        if not matched_cat_word: matched_cat_word = "drain/manhole"

    # 3. Resolve Ambiguity & Set Flags
    flag = ""
    if len(category_matches) == 1:
        category = category_matches[0]
    elif len(category_matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 4. Formulate Single-Sentence Reason
    if category == "Other" and flag == "NEEDS_REVIEW":
        if len(category_matches) > 1:
            reason = f"Multiple category triggers ({', '.join(category_matches)}) were found, requiring manual review."
        else:
            reason = "No definitive category keywords were found in the description."
    else:
        reason = f"Classified as {category} because the description explicitly mentions '{matched_cat_word}'."
        
    if priority == "Urgent":
        # Ensure it remains a single sentence by replacing period if needed or appending
        reason = reason.rstrip('.') + f" and assigned Urgent priority due to the severity keyword '{matched_urgent_word}'."
    elif not reason.endswith('.'):
        reason += "."
        
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
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames if reader.fieldnames else []
            
            # Ensure our output columns exist
            for col in ["category", "priority", "reason", "flag"]:
                if col not in fieldnames:
                    fieldnames.append(col)
                    
            rows = []
            for row in reader:
                try:
                    if not row.get("description"):
                        row["category"] = "Other"
                        row["flag"] = "NEEDS_REVIEW"
                        row["reason"] = "Description is missing or null."
                    else:
                        classification = classify_complaint(row)
                        row.update(classification)
                except Exception as e:
                    row["category"] = "Other"
                    row["flag"] = "NEEDS_REVIEW"
                    row["reason"] = f"Failed to parse or classify row due to error: {e}"
                
                rows.append(row)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
    except Exception as e:
        print(f"Fatal error processing batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
