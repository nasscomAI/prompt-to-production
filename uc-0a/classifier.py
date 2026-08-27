"""
UC-0A — Complaint Classifier
Implemented based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md.
    Returns: dict with appended keys: category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Enforcement: Exact Category string
    categories = []
    if "pothole" in desc:
        categories.append("Pothole")
    if "flood" in desc or "water" in desc:
        categories.append("Flooding")
    if "light" in desc or "dark" in desc:
        categories.append("Streetlight")
    if "garbage" in desc or "waste" in desc or "animal" in desc or "smell" in desc:
        categories.append("Waste")
    if "music" in desc or "noise" in desc:
        categories.append("Noise")
    if "road" in desc or "crack" in desc or "surface" in desc or "manhole" in desc or "footpath" in desc:
        categories.append("Road Damage")
    if "heritage" in desc:
        categories.append("Heritage Damage")
    if "drain" in desc or "blocked" in desc:
        categories.append("Drain Blockage")
        
    category = "Other"
    flag = ""
    if len(categories) == 1:
        category = categories[0]
    elif len(categories) > 1:
        # Resolve some overlaps or mark ambiguous
        if "Heritage Damage" in categories and "Streetlight" in categories:
            category = "Other"
            flag = "NEEDS_REVIEW"
        elif "Flooding" in categories and "Drain Blockage" in categories:
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Enforcement: Priority Urgent if severity keywords present
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            break
            
    # 3. Enforcement: Reason must be one sentence citing words
    words_cited = " and ".join([w for w in desc.split()[:3]]) # Just pick first few words as a citation mock
    reason = f"The description contains '{words_cited}' which maps to this category."
    
    # Optional enhancement: Make reason more specific based on matched category
    if category != "Other":
        matched_word = categories[0].lower() if categories else "keywords"
        reason = f"The description mentions words related to {matched_word} justifying the classification."
    if priority == "Urgent":
        reason = f"The priority is Urgent because the description mentions severe keywords."
    if flag == "NEEDS_REVIEW":
        reason = "The description contains overlapping or unclear issues."

    return {
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
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                fieldnames = []
                
            # Add new columns
            out_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
            
            rows_to_write = []
            for row in reader:
                # Handle empty or malformed row
                if not row or not any(row.values()):
                    continue
                    
                classification = classify_complaint(row)
                row.update(classification)
                rows_to_write.append(row)
                
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
    except Exception as e:
        print(f"Error processing batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

