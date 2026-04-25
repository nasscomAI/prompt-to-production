"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    # Error handling: if input is malformed or description is too short
    if not description or not isinstance(description, str) or len(description.strip()) < 5:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or too short to classify.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Priority logic
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    urgent_word = None
    for word in urgent_keywords:
        if word in desc_lower:
            priority = "Urgent"
            urgent_word = word
            break
            
    # Category logic
    categories = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogging", "overflow"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "garbage", "trash", "rubbish"],
        "Noise": ["noise", "loud", "music"],
        "Road Damage": ["road damage", "cracked road", "broken road"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat", "temperature"],
        "Drain Blockage": ["drain", "block", "clog"]
    }
    
    category = "Other"
    cat_word = None
    for cat, words in categories.items():
        for word in words:
            if word in desc_lower:
                category = cat
                cat_word = word
                break
        if category != "Other":
            break
            
    # Flag and Reason logic
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Category could not be determined confidently from the description alone."
    else:
        reason = f"Classified as {category} because description mentions '{cat_word}'."
        
    if priority == "Urgent":
        reason += f" Priority escalated to Urgent due to keyword '{urgent_word}'."
        
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
    """
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Skip completely empty rows
                    if not any(row.values()):
                        continue
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    print(f"Error processing row {row_num}: {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        return
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        return
        
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file '{output_path}': {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
