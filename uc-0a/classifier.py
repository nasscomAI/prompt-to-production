"""
UC-0A — Complaint Classifier
Implementation based on AGENTS.md and skills.md requirements.
"""
import argparse
import csv
import sys

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single complaint row based on text analysis.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Defaults
    category = "Other"
    priority = "Standard"
    flag = ""
    reason_word = None
    
    # 1. Evaluate Priority based on exact severity keywords
    for word in SEVERITY_KEYWORDS:
        if word in desc:
            priority = "Urgent"
            reason_word = word
            break
            
    # 2. Evaluate Category based on simple heuristic matching
    if "pothole" in desc:
        category = "Pothole"
        if not reason_word: reason_word = "pothole"
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
        if not reason_word: reason_word = "flood"
    elif "drain" in desc or "manhole" in desc:
        category = "Drain Blockage"
        if not reason_word: reason_word = "drain"
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
        if not reason_word: reason_word = "light"
    elif "waste" in desc or "garbage" in desc or "animal" in desc or "dump" in desc:
        category = "Waste"
        if not reason_word: reason_word = "waste/garbage"
    elif "music" in desc or "noise" in desc:
        category = "Noise"
        if not reason_word: reason_word = "noise/music"
    elif "crack" in desc or "road surface" in desc or "footpath" in desc:
        category = "Road Damage"
        if not reason_word: reason_word = "road surface/crack"
    elif "heritage" in desc:
        category = "Heritage Damage"
        if not reason_word: reason_word = "heritage"
    elif "heat" in desc:
        category = "Heat Hazard"
        if not reason_word: reason_word = "heat"
        
    # 3. Handle Ambiguity & Flags
    if category == "Other" or not desc.strip():
        flag = "NEEDS_REVIEW"
        
    # 4. Construct Exact 1-Sentence Reason citing specific words
    if reason_word:
        reason = f"The description was classified as {category} with {priority} priority because it contains the specific word '{reason_word}'."
    else:
        reason = "The complaint lacks specific recognized identifiers and needs manual verification."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, processes each row via classify_complaint, 
    and writes results to a new output CSV safely.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print(f"Error: No fieldnames found in {input_path}")
                return
                
            # Maintain original columns plus the 4 new ones
            out_fields = fieldnames + ["category", "priority", "reason", "flag"]
            
            # Remove any duplicates in fieldnames while preserving order
            out_fields = list(dict.fromkeys(out_fields))
            
            rows = list(reader)
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=out_fields)
            writer.writeheader()
            
            for row in rows:
                try:
                    result = classify_complaint(row)
                    row.update(result)
                except Exception as eval_err:
                    # Error Handling requirement per skills.md
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = f"Parse failure during classification: {str(eval_err)}."
                    row["flag"] = "NEEDS_REVIEW"
                    
                writer.writerow(row)
    except Exception as e:
        print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input complaints CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Classification results successfully written to {args.output}")
