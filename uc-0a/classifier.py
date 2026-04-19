"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on strict RICE rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Category
    # Must strictly match allowed values
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging", "knee-deep"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "garbage", "trash", "smell", "dead animal"],
        "Noise": ["noise", "loud", "music"],
        "Road Damage": ["road surface", "cracked", "sinking", "manhole", "footpath", "tiles broken", "upturned"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain", "block"]
    }
    
    matched_categories = []
    matched_words = []
    
    for cat, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in description:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_words.append(keyword)
                    
    category = "Other"
    flag = ""
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 2. Determine Priority
    # Must be Urgent if severity keywords present
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    urgent_reason_word = None
    
    for word in severity_keywords:
        if word in description:
            priority = "Urgent"
            urgent_reason_word = word
            break
            
    # 3. Formulate Reason (One sentence, citing specific words)
    reason_parts = []
    if category != "Other":
        reason_parts.append(f"Categorized as {category} because it mentions '{matched_words[0]}'")
    else:
        reason_parts.append("Category is ambiguous or missing clear keywords")
        
    if priority == "Urgent":
        reason_parts.append(f"and priority is Urgent due to severity keyword '{urgent_reason_word}'.")
    else:
        reason_parts.append("and priority is Standard as no severity keywords were found.")
        
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                logging.error("Input file has no headers or is empty.")
                return
                
            output_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
            
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
                writer.writeheader()
                
                for row in reader:
                    try:
                        if not row or not any(row.values()):
                            row["flag"] = "ERROR_NULL_ROW"
                            writer.writerow(row)
                            continue
                            
                        classification = classify_complaint(row)
                        row.update({
                            "category": classification["category"],
                            "priority": classification["priority"],
                            "reason": classification["reason"],
                            "flag": classification["flag"]
                        })
                        writer.writerow(row)
                    except Exception as e:
                        logging.warning(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")
                        row["flag"] = "ERROR"
                        writer.writerow(row)
                        
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_path}")
    except Exception as e:
        logging.error(f"Failed during batch classification: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
