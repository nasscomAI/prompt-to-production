"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE schema rules.
    Returns: dict with updated category, priority, reason, flag
    """
    desc = str(row.get("description", "")).lower()
    
    urgency_kw = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    urgent_found = [kw for kw in urgency_kw if kw in desc]
    priority = "Urgent" if urgent_found else "Standard"
    
    cat_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging", "overflow"],
        "Streetlight": ["streetlight", "street light", "lamp", "lighting", "dark"],
        "Waste": ["waste", "trash", "garbage", "rubbish"],
        "Noise": ["noise", "loud", "music"],
        "Road Damage": ["crack", "road damage", "damaged road"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat", "temperature", "sun"],
        "Drain Blockage": ["drain", "blockage", "clogged", "sewer"]
    }
    
    matches = []
    reason_words = []
    
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in desc:
                if cat not in matches:
                    matches.append(cat)
                reason_words.append(kw)
                break
                
    flag = ""
    if not matches:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_text = "No clear category keywords found in description."
    elif len(matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_text = f"Ambiguous description matching multiple categories: {', '.join(reason_words)}."
    else:
        category = matches[0]
        reason_text = f"Classified based on mentioned keyword '{reason_words[0]}'."
        
    if urgent_found:
        reason_text += f" Escalated to Urgent due to severity keyword '{urgent_found[0]}'."
        
    # Make sure we don't overwrite if it's already a complete dict but we return what we need
    # The prompt actually says return dict with keys: complaint_id, category, priority, reason, flag
    out = dict(row)
    out["category"] = category
    out["priority"] = priority
    out["reason"] = reason_text
    out["flag"] = flag
    return out


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            for col in ["category", "priority", "reason", "flag"]:
                if col not in fieldnames:
                    fieldnames.append(col)
                    
            rows = []
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    rows.append(classified_row)
                except Exception as e:
                    row["category"] = "Other"
                    row["priority"] = "Standard"
                    row["reason"] = f"Error: {str(e)}"
                    row["flag"] = "NEEDS_REVIEW"
                    rows.append(row)
                    
        with open(output_path, 'w', encoding='utf-8', newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
    except Exception as e:
        print(f"File processing error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
