"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    comp_id = row.get("complaint_id", "")
    desc = row.get("description", "")
    
    default_result = {
        "complaint_id": comp_id,
        "category": "Other",
        "priority": "Low",
        "reason": "Input was malformed or description too short.",
        "flag": "NEEDS_REVIEW"
    }
    
    if not isinstance(desc, str) or len(desc.strip()) < 5:
        return default_result

    desc_lower = desc.lower()
    
    # Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    matched_priority_kw = None
    for kw in urgent_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            matched_priority_kw = kw
            break
            
    # Category mapping
    categories = {
        "Pothole": ["pothole", "crater", "hole in road"],
        "Flooding": ["flood", "waterlogging", "submerged", "water"],
        "Streetlight": ["streetlight", "dark", "lamp", "light"],
        "Waste": ["waste", "garbage", "trash", "rubbish"],
        "Noise": ["noise", "loud", "music", "party"],
        "Road Damage": ["crack", "road damage", "broken surface"],
        "Heritage Damage": ["heritage", "monument", "statue"],
        "Heat Hazard": ["heat", "heatwave"],
        "Drain Blockage": ["drain", "blocked", "sewer"]
    }
    
    matched_category = "Other"
    matched_word = ""
    matches = 0
    
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in desc_lower:
                if matched_category == "Other":
                    matched_category = cat
                    matched_word = kw
                    matches = 1
                elif matched_category != cat:
                    matches += 1
                break
                
    flag = ""
    if matches > 1:
        flag = "NEEDS_REVIEW"
        
    if matched_word:
        reason = f"Classified as {matched_category} because description contains the word '{matched_word}'."
        if priority == "Urgent":
            reason += f" Marked Urgent due to keyword '{matched_priority_kw}'."
    elif priority == "Urgent":
        reason = f"Classified as Other but marked Urgent due to keyword '{matched_priority_kw}'."
    else:
        reason = "Classified as Other as no specific category keywords were found."

    return {
        "complaint_id": comp_id,
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except Exception as e:
        logging.error(f"Failed to read input file {input_path}: {e}")
        # Ensure output file is created even if reading fails completely
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
        return

    results = []
    for i, row in enumerate(rows):
        if not row:
            continue
        try:
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            logging.error(f"Row {i} failed: {e}")

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        logging.error(f"Failed to write output file {output_path}: {e}")


if __name__ == "__main__":
    import argparse
    import csv
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
