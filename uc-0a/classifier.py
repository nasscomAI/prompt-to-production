"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", 
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "potholes"],
    "Flooding": ["flood", "waterlogging", "submerged", "overflow"],
    "Streetlight": ["streetlight", "dark", "no light", "bulb"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "litter"],
    "Noise": ["noise", "loud", "music", "construction sound", "speaker"],
    "Road Damage": ["road damage", "broken road", "crack", "paving"],
    "Heritage Damage": ["heritage", "monument", "statue", "ruin"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke", "temperature"],
    "Drain Blockage": ["drain", "clog", "sewage", "block", "gutter", "choked"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md.
    Returns: dict with updated keys: category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Priority
    priority = "Standard"
    matched_severity = None
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', description):
            priority = "Urgent"
            matched_severity = kw
            break
            
    # 2. Determine Category
    category = "Other"
    matched_cat_kw = None
    flag = "NEEDS_REVIEW"
    
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in description:
                category = cat
                matched_cat_kw = kw
                flag = ""
                break
        if category != "Other":
            break
            
    # 3. Formulate Reason (must cite specific words)
    reason_parts = []
    if category != "Other":
        reason_parts.append(f"Category set to {category} because description mentions '{matched_cat_kw}'.")
    else:
        reason_parts.append("Category could not be determined from the description alone.")
        
    if priority == "Urgent":
        reason_parts.append(f"Priority escalated to Urgent due to severity keyword '{matched_severity}'.")
    else:
        reason_parts.append("Priority set to Standard as no severity keywords were found.")
        
    reason = " ".join(reason_parts)
    
    # Build output row
    out_row = dict(row)
    out_row["category"] = category
    out_row["priority"] = priority
    out_row["reason"] = reason
    out_row["flag"] = flag
    
    return out_row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV based on skills.md.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Error: Input CSV contains no headers.")
                return
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    # Add required columns if not present
    for col in ["category", "priority", "reason", "flag"]:
        if col not in fieldnames:
            fieldnames.append(col)
            
    results = []
    for row in rows:
        try:
            # Use classify_complaint skill per row
            classified = classify_complaint(row)
            results.append(classified)
        except Exception as e:
            # Error handling: do not crash on bad rows
            out_row = dict(row)
            out_row["category"] = "Other"
            out_row["priority"] = "Standard"
            out_row["reason"] = f"Processing failed: {str(e)}"
            out_row["flag"] = "NEEDS_REVIEW"
            results.append(out_row)
            
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
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
