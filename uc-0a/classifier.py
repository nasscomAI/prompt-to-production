"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Keyword mapping for exact categories (as defined in agents.md)
    categories = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "light", "dark", "sparking"],
        "Waste": ["garbage", "waste", "smell", "animal", "dump"],
        "Noise": ["music", "noise", "loud"],
        "Road Damage": ["crack", "sink", "broken", "surface", "footpath", "road"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain", "manhole", "block"]
    }
    
    # 1. Detect categories
    matched_cats = []
    cited_words = []
    for cat, keywords in categories.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc) or kw in desc:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                cited_words.append(kw)
                
    category = "Other"
    flag = ""
    
    # Ambiguity check
    if len(matched_cats) == 1:
        category = matched_cats[0]
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 2. Determine Priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    priority = "Standard"
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            cited_words.append(kw)
            break
            
    # Enforcement: If ambiguous, Flag: NEEDS_REVIEW, Priority: Low
    if flag == "NEEDS_REVIEW":
        priority = "Low"
        
    # 3. Create Reason
    reason_words = list(set(cited_words))
    if reason_words:
        cited_str = ", ".join(f"'{w}'" for w in reason_words[:3])  # cite up to 3 words
        reason = f"Classification determined by citing the words {cited_str} from the description."
    else:
        reason = "Insufficient specific keywords identified to confidently classify."
        
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
            fieldnames = reader.fieldnames or []
            
            # Ensure our output headers are available (keeping existing + new columns)
            output_headers = fieldnames + ["category", "priority", "reason", "flag"]
            output_headers = list(dict.fromkeys(output_headers))
            
            classified_rows = []
            for row in reader:
                try:
                    result = classify_complaint(row)
                    row.update({
                        "category": result["category"],
                        "priority": result["priority"],
                        "reason": result["reason"],
                        "flag": result["flag"]
                    })
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    row.update({
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error during processing: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                
                classified_rows.append(row)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_headers)
            writer.writeheader()
            writer.writerows(classified_rows)
            
    except Exception as e:
        print(f"Failed to run batch_classify: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
