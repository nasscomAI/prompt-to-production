"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

# Severity keywords mapping from agents.md enforcement rules
URGENT_KEYWORDS = [
    'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'
]

# Classification schema map to assist rule-based classification
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "water", "inundate"],
    "Streetlight": ["streetlight", "light", "dark", "sparking"],
    "Waste": ["waste", "garbage", "trash", "animal", "smell", "dump"],
    "Noise": ["noise", "loud", "music"],
    "Road Damage": ["road", "crack", "sinking", "manhole", "footpath", "broken", "tiles"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "temperature"],
    "Drain Blockage": ["drain", "clog", "blockage"]
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    # Defensive check
    if not isinstance(row, dict) or 'description' not in row:
        return {
            "category": "Other", 
            "priority": "Low", 
            "reason": "Missing description or corrupted record.", 
            "flag": "NEEDS_REVIEW"
        }

    desc = row.get("description", "").lower()
    
    category = "Other"
    priority = "Standard"
    reason = "Could not identify a specific category."
    flag = "NEEDS_REVIEW"
    
    # 1. Determine priority
    found_urgent_words = [w for w in URGENT_KEYWORDS if w in desc]
    if found_urgent_words:
        priority = "Urgent"

    # 2. Determine Category
    matched_categories = []
    reason_words = []
    
    for cat, words in CATEGORY_KEYWORDS.items():
        matched = [w for w in words if w in desc]
        if matched:
            matched_categories.append(cat)
            reason_words.extend(matched)

    # Resolve Classification & Reason Formulation
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        reason = f"Classified as {category} because description mentions '{reason_words[0]}'."
    elif len(matched_categories) > 1:
        # Resolve collisions or flag for review
        category = matched_categories[0] # taking the first as default
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous: matched multiple categories ({', '.join(matched_categories)})."
    
    if found_urgent_words:
        reason += f" Priority marked Urgent due to '{found_urgent_words[0]}'."

    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
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
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("CSV input has no headers.")
            
            # Extend fields
            output_fields = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]
            
            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_fields)
                writer.writeheader()
                
                rows_processed = 0
                for row in reader:
                    try:
                        classification = classify_complaint(row)
                        # ensure safe updates
                        for k, v in classification.items():
                            if k != 'complaint_id':
                                row[k] = v
                        writer.writerow(row)
                        rows_processed += 1
                    except Exception as loop_err:
                        # Graceful failure on record level
                        row["category"] = "Other"
                        row["priority"] = "Low"
                        row["reason"] = f"Error classifying row: {str(loop_err)}"
                        row["flag"] = "NEEDS_REVIEW"
                        writer.writerow(row)
                        rows_processed += 1
                        
        print(f"Successfully processed {rows_processed} records.")
    except FileNotFoundError:
        print(f"FAILED: The input file {input_path} was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"FAILED: An error occurred during batch processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
