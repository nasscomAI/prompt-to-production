"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE rules.
    """
    description = row.get("description", "").strip()
    desc_lower = description.lower()
    complaint_id = row.get("complaint_id", "Unknown")

    # 1. Enforcement: Priority must be Urgent if description contains specific keywords
    # Keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    matched_urgent = [kw for kw in urgent_keywords if kw in desc_lower]
    if matched_urgent:
        priority = "Urgent"

    # 2. Enforcement: Category must be exactly one of the allowed taxonomy
    allowed_categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    
    # Simple keyword-based category matching (can be improved with better mappings)
    category_keywords = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogging", "inundation", "submerged"],
        "Streetlight": ["streetlight", "street light", "lamp", "darkness"],
        "Waste": ["waste", "garbage", "trash", "dump", "litter", "dead animal"],
        "Noise": ["noise", "loud", "music", "speaker"],
        "Drain Blockage": ["drain", "sewer", "clog", "blockage", "manhole"],
        "Heritage Damage": ["heritage", "monument", "historic"],
        "Heat Hazard": ["heat", "hot", "sunstroke"],
        "Road Damage": ["road", "asphalt", "crack", "surface", "pavement", "footpath", "tile"]
    }

    category = "Other"
    matched_category_kw = ""
    
    # Priority matching order: check specific categories first
    for cat, kws in category_keywords.items():
        for kw in kws:
            if kw in desc_lower:
                category = cat
                matched_category_kw = kw
                break
        if category != "Other":
            break

    # 3. Enforcement: Refusal condition - flag genuinely ambiguous cases
    flag = ""
    if category == "Other" or not description:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No clear category detected from the description."
    else:
        # 4. Enforcement: Reason field must cite specific words
        cited_words = [matched_category_kw] + matched_urgent
        reason = f"Classified because description mentions '{', '.join(set(cited_words))}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint per row, write output CSV.
    """
    if not os.path.exists(input_path):
        logging.error(f"Input file not found: {input_path}")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Skills: apply classify_complaint per row
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    logging.error(f"Error processing row {row.get('complaint_id')}: {e}")
                    # Skills: produce output even if some rows fail
                    continue
        
        if not results:
            logging.warning("No valid complaints processed.")
            return

        # Write to output CSV
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        logging.info(f"Successfully processed {len(results)} rows. Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Batch processing failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
