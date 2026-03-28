"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the R.I.C.E. enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = str(row.get("description", "")).lower()
    
    # Priority severity keywords
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    # Category definition based on keyword mapping (ordered by specificity)
    categories = {
        "Heritage Damage": ["heritage", "monument", "historic", "statue"],
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogged", "water logging", "rainwater", "submerged"],
        "Drain Blockage": ["drain", "blocked", "clogged", "sewer", "blockage"],
        "Streetlight": ["streetlight", "lamp", "darkness", "substation", "light", "tripped"],
        "Waste": ["waste", "garbage", "trash", "rubbish"],
        "Noise": ["noise", "loud", "music", "wedding band", "amplifier", "speaker"],
        "Heat Hazard": ["heat", "sunstroke", "temperature"],
        "Road Damage": ["road", "crack", "broken", "buckled", "subsided", "paving", "footpath", "cobblestones"]
    }

    # Extract severity
    found_severity_kw = None
    for kw in severity_keywords:
        if kw in description:
            found_severity_kw = kw
            break
            
    # Extract Category
    found_category = "Other"
    found_category_kw = None
    
    for cat, kws in categories.items():
        for kw in kws:
            if kw in description:
                found_category = cat
                found_category_kw = kw
                break
        if found_category != "Other":
            break
            
    # Apply R.I.C.E Enforcement Rules
    if found_category == "Other" or not description.strip():
        # Rule: Ambiguous or Other
        row["category"] = "Other"
        row["priority"] = "Low"
        row["reason"] = "Description is genuinely ambiguous and does not match specific category keywords."
        row["flag"] = "NEEDS_REVIEW"
    else:
        row["category"] = found_category
        row["flag"] = ""
        
        # Rule: Priority assignment based on rules
        if found_severity_kw:
            row["priority"] = "Urgent"
            row["reason"] = f"Classified as {found_category} ('{found_category_kw}') and prioritised as Urgent due to severity keyword '{found_severity_kw}'."
        else:
            row["priority"] = "Standard"
            row["reason"] = f"Classified as {found_category} due to the mention of '{found_category_kw}'."

    return row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely process rows, flag nulls/errors, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            
            # Ensure target output columns are present
            target_cols = ['category', 'priority', 'reason', 'flag']
            for col in target_cols:
                if col not in fieldnames:
                    fieldnames.append(col)
                    
            rows = []
            for row in reader:
                try:
                    # Apply classify_complaint
                    classified_row = classify_complaint(row)
                    rows.append(classified_row)
                except Exception as e:
                    print(f"Warning: Failed to classify row due to error: {e}")
                    row['category'] = "Other"
                    row['priority'] = "Low"
                    row['reason'] = f"Processing error: {str(e)}"
                    row['flag'] = "DATA_ERROR"
                    rows.append(row)
                
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            out_fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            # Using extrasaction='ignore' means any fields in the row dict that aren't in out_fieldnames will be dropped.
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
            
    except Exception as e:
        print(f"Error during batch classification: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
