"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import logging

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to agents.md rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", row.get("id", ""))
    
    # Priority Enforcement
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if kw in description]
    priority = "Urgent" if found_urgent else "Standard"

    # Category Mapping Heuristics
    cat_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlog"],
        "Streetlight": ["streetlight", "dark street", "no light"],
        "Waste": ["waste", "garbage", "trash"],
        "Noise": ["noise", "loud", "music"],
        "Road Damage": ["road crack", "broken road", "sinkhole", "road damage"],
        "Heritage Damage": ["heritage", "monument ruin", "graffiti"],
        "Heat Hazard": ["heatwave", "extreme heat", "heat hazard"],
        "Drain Blockage": ["drain block", "clogged drain", "sewage leak"]
    }
    
    matched_cats = []
    reason_words = []
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in description:
                matched_cats.append(cat)
                reason_words.append(kw)
                break
                
    # Ambiguity flag and refusal condition
    if len(matched_cats) == 1:
        category = matched_cats[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    reason_words.extend(found_urgent)
    if reason_words:
        reason = f"Description cites: {', '.join(set(reason_words))}."
    else:
        reason = "Cannot clearly determine category or priority from description alone."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must handle errors gracefully and skip malformed rows.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    try:
        with open(input_path, 'r', encoding='utf-8-sig') as f_in:
            reader = csv.DictReader(f_in)
            rows = list(reader)
    except Exception as e:
        logging.error(f"Failed to read input file {input_path}: {e}")
        return

    results = []
    for idx, row in enumerate(rows):
        try:
            classified = classify_complaint(row)
            results.append(classified)
        except Exception as e:
            logging.error(f"Row {idx+1} failed classification: {e}")

    if not results:
        logging.warning("No valid results to write out.")
        return

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f_out:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        logging.error(f"Failed to write results to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

