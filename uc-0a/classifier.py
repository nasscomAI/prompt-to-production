"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority Keywords mapping
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_sev = [kw for kw in severity_keywords if re.search(r'\b' + kw + r'\b', desc)]
    priority = "Urgent" if found_sev else "Standard"
    
    # Category Keywords Mapping
    cat_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "lights out", "dark"],
        "Waste": ["waste", "garbage", "dead animal", "smell", "dumped"],
        "Noise": ["noise", "music"],
        "Road Damage": ["road surface", "cracked", "sinking", "manhole", "broken", "footpath"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain"]
    }
    
    cat_matches = {}
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in desc:
                cat_matches[cat] = kw
                break # Just record the first keyword that matches for the category
                
    # Ambiguity check
    if len(cat_matches) == 1:
        category, cat_word = list(cat_matches.items())[0]
        flag = ""
    elif len(cat_matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Reason sentence formulation
    if flag == "NEEDS_REVIEW":
        if len(cat_matches) > 1:
            quoted_words = ", ".join([f"'{v}'" for v in cat_matches.values()])
            reason = f"Category is ambiguous because the description contains multiple matching keywords: {quoted_words}."
        else:
            reason = "Category cannot be determined from the description alone due to a lack of explicit keywords."
    else:
        if priority == "Urgent":
            reason = f"Classified as {category} and Urgent because the description explicitly mentions '{cat_word}' and '{found_sev[0]}'."
        else:
            reason = f"Classified as {category} because the description explicitly mentions '{cat_word}'."
            
    # Output copy
    out_row = dict(row)
    out_row["category"] = category
    out_row["priority"] = priority
    out_row["reason"] = reason
    out_row["flag"] = flag
    
    return out_row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV is empty or lacks headers.")
                
            fieldnames = list(reader.fieldnames)
            # Add new fields ensuring order without duplication
            for nf in ["category", "priority", "reason", "flag"]:
                if nf not in fieldnames:
                    fieldnames.append(nf)
                    
            for row in reader:
                try:
                    if not row.get("description") or not str(row.get("description")).strip():
                        # Null handling
                        r_out = dict(row)
                        r_out["category"] = "Other"
                        r_out["priority"] = "Low"
                        r_out["reason"] = "Description is empty or missing."
                        r_out["flag"] = "NEEDS_REVIEW"
                        results.append(r_out)
                        continue
                        
                    results.append(classify_complaint(row))
                except Exception as e:
                    r_out = dict(row)
                    r_out["category"] = "Other"
                    r_out["priority"] = "Low"
                    r_out["reason"] = f"Row processing failed: {str(e)}."
                    r_out["flag"] = "ERROR"
                    results.append(r_out)
                    
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Batch classification failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
