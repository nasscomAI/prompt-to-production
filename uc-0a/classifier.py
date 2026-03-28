"""
UC-0A — Complaint Classifier
Starter file. Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    description_lower = description.lower()
    
    # Default ambiguous classification
    category = "Other"
    priority = "Low"
    flag = "NEEDS_REVIEW"
    reason = "Category cannot be determined from the description alone."

    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. PRIORITY RULES
    # Priority can be only from "Urgent · Standard · Low"
    # Priority must be Urgent if description contains any of the following triggers:"injury,child,school,hospital"
    triggers = ["injury", "child", "school", "hospital"]
    matched_triggers = [t for t in triggers if t in description_lower]
    
    if matched_triggers:
        priority = "Urgent"
    else:
        priority = "Standard"

    # 2. CATEGORY RULES
    # "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water", "rain"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "smell", "dump", "dead animal"],
        "Noise": ["noise", "loud", "music", "party"],
        "Road Damage": ["crack", "road surface", "broken", "footpath", "sinking"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "hot"],
        "Drain Blockage": ["drain", "blocked", "manhole"]
    }

    matched_categories = []
    matched_keywords = []

    for cat, kws in category_keywords.items():
        for kw in kws:
            if kw in description_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                matched_keywords.append(kw)
                break

    # 3. REASON AND FLAG RULES
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = "" # Clear flag when confidently determined
        # "Every output row must include a reason field citing specific words from the description"
        reason = f"Classified based on the specific word '{matched_keywords[0]}' in description."
    else:
        # "If the category cannot be determined from the description alone, output category: Other and flag: NEEDS_REVIEW,Priority:Low"
        category = "Other"
        priority = "Low"
        flag = "NEEDS_REVIEW"
        if len(matched_categories) > 1:
            reason = f"Ambiguous between multiple categories caused by words: {', '.join(matched_keywords)}."
        else:
            reason = "Category cannot be determined from the description alone without matching words."

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
    """
    if not os.path.exists(input_path):
        print(f"Error: Cannot find input file {input_path}", file=sys.stderr)
        return
        
    output_rows = []
    
    # Process file
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Ensure proper fieldnames setup
            fieldnames = reader.fieldnames if reader.fieldnames else []
            for field in ['category', 'priority', 'reason', 'flag']:
                if field not in fieldnames:
                    fieldnames.append(field)
                    
            for row in reader:
                try:
                    result = classify_complaint(row)
                    row.update(result)
                    output_rows.append(row)
                except Exception as e:
                    print(f"Warning: Failed to process row ID {row.get('complaint_id', 'unknown')}: {e}", file=sys.stderr)
                    # Fallback output
                    row.update({
                        "category": "Other", 
                        "priority": "Low", 
                        "reason": "System error during classification.", 
                        "flag": "NEEDS_REVIEW"
                    })
                    output_rows.append(row)
    except Exception as e:
        print(f"Failed to read from file {input_path}: {e}", file=sys.stderr)
        return

    # Write file
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in output_rows:
                writer.writerow(row)
                
    except Exception as e:
        print(f"Failed to write results to {output_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
