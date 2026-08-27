"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Enforcement rule definitions derived from agents.md
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "crater"],
    "Flooding": ["flood", "flooded", "waterlogging", "submerged"],
    "Streetlight": ["streetlight", "streetlights", "dark", "no light", "lamp", "lights out"],
    "Waste": ["waste", "garbage", "trash", "dump", "rubbish"],
    "Noise": ["noise", "loud", "music", "speaker"],
    "Road Damage": ["road damage", "crack", "cracked", "broken road", "sinking"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    "Heat Hazard": ["heat", "heatwave", "temperature"],
    "Drain Blockage": ["drain", "blocked", "clog", "clogged", "sewer", "manhole"]
}

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row enforcing strict RICE rules.
    Returns: dict with all original keys plus appended category, priority, reason, flag.
    """
    description = row.get("description", "").lower()
    
    # Rule 2: Enforce Priority based on exact severity keywords
    priority = "Standard"
    urgent_match = None
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            urgent_match = kw
            break
            
    # Rule 1: Enforce Taxonomy / Category match
    matched_categories = []
    reason_kws = []
    
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in description:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    reason_kws.append(kw)
    
    # Rule 3 & 4: Reason extraction and Ambiguity Flagging
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
        reason_phrase = reason_kws[0]
        if urgent_match:
            reason = f"The description mentions '{reason_phrase}' and severity keyword '{urgent_match}'."
        else:
            reason = f"The description mentions the keyword '{reason_phrase}'."
    else:
        # Fallback for ambiguous or no-match complaints
        category = "Other"
        flag = "NEEDS_REVIEW"
        if len(matched_categories) > 1:
            cats_str = ", ".join(matched_categories)
            reason = f"Ambiguous complaint matching multiple categories: {cats_str}."
        elif not description.strip():
            reason = "Description is completely empty."
            priority = "Low"
        else:
            reason = "No explicitly authorized category keywords were found."
            
        if urgent_match:
            reason += f" Contains urgent severity keyword '{urgent_match}'."
            
    # Assemble output safely
    result = row.copy()
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint per row, write to results CSV.
    Safeguarded against crashes on bad rows.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                print("Error: Empty input file or missing headers")
                return
            
            rows = list(reader)
            
        # Ensure our extra columns exist in the output fields
        out_fields = list(reader.fieldnames)
        for field in ["category", "priority", "reason", "flag"]:
            if field not in out_fields:
                out_fields.append(field)
                
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fields)
            writer.writeheader()
            
            for row in rows:
                try:
                    classified = classify_complaint(row)
                    writer.writerow(classified)
                except Exception as e:
                    # Error handling enforcement
                    print(f"Warning: Failed to classify a row. Error: {e}")
                    err_row = row.copy()
                    for f in ["category", "priority", "reason", "flag"]:
                        if f not in err_row:
                            err_row[f] = ""
                            
                    err_row["category"] = "Other"
                    err_row["priority"] = "Low"
                    err_row["reason"] = f"Processing error: {str(e)}"
                    err_row["flag"] = "NEEDS_REVIEW"
                    writer.writerow(err_row)
                    
    except Exception as e:
        print(f"Fatal error during batch classification: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
