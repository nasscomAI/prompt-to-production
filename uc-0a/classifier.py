import argparse
import csv
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    RICE enforcement rules are reflected in this function's behaviour based on agents.md
    """
    description = str(row.get('description', '')).lower()
    
    # Check nulls/empty
    if not description.strip():
        return {
            'complaint_id': row.get('complaint_id', row.get('id', '')),
            'category': 'Other',
            'priority': 'Low',
            'reason': "The description provided was empty.",
            'flag': 'NEEDS_REVIEW'
        }
        
    URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    CATEGORY_KEYWORDS = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlog", "overflow", "submerged"],
        "Streetlight": ["streetlight", "light", "dark", "bulb"],
        "Waste": ["waste", "trash", "garbage", "rubbish", "dump"],
        "Noise": ["noise", "loud", "music", "party"],
        "Road Damage": ["road damage", "crack", "broken road", "uneven road"],
        "Heritage Damage": ["heritage", "monument", "statue", "ruin"],
        "Heat Hazard": ["heat", "sun", "burn", "temperature"],
        "Drain Blockage": ["drain", "block", "clog", "sewage"]
    }
    
    # Priority matching
    priority = "Standard"
    found_urgent_keyword = None
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            found_urgent_keyword = kw
            break
            
    # Category matching
    matched_categories = []
    matched_keyword_for_reason = ""
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in description:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_keyword_for_reason = kw
                break
                
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = "OK"
        reason_keyword = matched_keyword_for_reason
    else:
        # Genuinely ambiguous (0 or >1 matches)
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_keyword = "ambiguous or multiple issues"
        
    # Extracted reason citing specific words (one sentence long)
    if priority == "Urgent" and category != "Other":
        reason = f"The description contains '{reason_keyword}' indicating a {category} issue, and urgency is triggered by '{found_urgent_keyword}'."
    elif priority == "Urgent":
        reason = f"The issue is prompted as Urgent due to '{found_urgent_keyword}', but the specific category remains {reason_keyword}."
    else:
        if category != "Other":
            reason = f"The description mentions '{reason_keyword}', which designates it as a {category} problem."
        else:
            reason = "The description lacked specific or unique keywords to accurately assign exactly one category."

    return {
        'complaint_id': row.get('complaint_id', row.get('id', '')),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file is missing or unreadable: {input_path}")
        
    results = []
    
    # Read the data
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV is empty or malformed.")
            
        for row_num, row in enumerate(reader, start=1):
            try:
                # Malformed rows check
                if not row or all(v is None or str(v).strip() == '' for v in row.values()):
                    logging.warning(f"Skipping malformed or empty row at line {row_num + 1}")
                    continue
                    
                classification = classify_complaint(row)
                
                # Combine original row with classification results
                result_row = row.copy()
                result_row.update(classification)
                results.append(result_row)
                
            except Exception as e:
                logging.warning(f"Failed to process row at line {row_num + 1}: {e}")
                
    if not results:
        logging.warning("No rows were successfully processed.")
        
    # Write the output if we have results
    if results:
        # Extract unique field names, honoring the original ones + generated keys
        fieldnames = list(results[0].keys())
        for f in ['category', 'priority', 'reason', 'flag']:
            if f not in fieldnames:
                fieldnames.append(f)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    try:
        batch_classify(args.input, args.output)
        print(f"Done. Results written to {args.output}")
    except Exception as e:
        logging.error(f"Execution failed: {e}")
