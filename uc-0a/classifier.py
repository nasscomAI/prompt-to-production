"""
UC-0A — Complaint Classifier
Implementation based on rules defined in agents.md and skills.md.
"""
import argparse
import csv
import sys
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # 1. Enforcement mapping for Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if re.search(rf"\b{kw}\b", description)]
    
    priority = "Urgent" if found_urgent else "Standard"

    # 2. Enforcement mapping for Category
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood"],
        "Streetlight": ["streetlight", "lights out", "dark"],
        "Waste": ["garbage", "waste", "dead animal", "dumped"],
        "Noise": ["music", "noise"],
        "Road Damage": ["road surface", "cracked", "manhole", "footpath", "tiles broken"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain blocked", "drainage"]
    }
    
    matched_cats = []
    matched_kw = None
    for cat, kws in category_keywords.items():
        for kw in kws:
            if kw in description:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                    if not matched_kw:
                        matched_kw = kw
    
    flag = ""
    # 3. Identify Category and Handle Ambiguity
    if len(matched_cats) == 1:
        category = matched_cats[0]
    else:
        # Ambiguous or unidentified cases
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 4. Enforce Context Reason
    reason_parts = []
    if category != "Other":
        reason_parts.append(f"Categorized as {category} because it mentions '{matched_kw}'.")
    else:
        reason_parts.append(f"Requires review due to ambiguous or unidentified topic.")
        
    if priority == "Urgent":
        reason_parts.append(f"Priority is Urgent because it explicitly mentions '{found_urgent[0]}'.")
    else:
        reason_parts.append("Priority is Standard as no severe hazard keywords were detected.")
        
    reason = " ".join(reason_parts)

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
    results = []
    fieldnames = []
    
    # Read the input CSV
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV is empty or has no header.")
            
            # Persist original fields, prepare for appending results
            fieldnames = list(reader.fieldnames)
            for f in ["category", "priority", "reason", "flag"]:
                if f not in fieldnames:
                    fieldnames.append(f)
                    
            for row in reader:
                try:
                    classified_data = classify_complaint(row)
                    row.update(classified_data)
                except Exception as e:
                    # Skill error handling: row fails to classify -> flag: NEEDS_REVIEW
                    row["category"] = "Other"
                    row["priority"] = "Standard"
                    row["reason"] = f"Processing error: {str(e)}"
                    row["flag"] = "NEEDS_REVIEW"
                results.append(row)
                
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Write the output CSV
    try:
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file '{output_path}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Classified {args.input} and wrote to {args.output}")
