"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "hole in road"],
    "Flooding": ["flood", "waterlogging", "inundation"],
    "Streetlight": ["streetlight", "street light", "lamp", "dark"],
    "Waste": ["waste", "garbage", "trash", "dump"],
    "Noise": ["noise", "loud", "sound", "volume"],
    "Road Damage": ["road damage", "pavement", "crack"],
    "Heritage Damage": ["heritage", "monument", "statue", "old building"],
    "Heat Hazard": ["heat", "hot", "sunstroke", "exhaustion"],
    "Drain Blockage": ["drain", "sewage", "gutter", "blockage"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Identify Category
    category = "Other"
    flag = ""
    found_categories = []
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in description for kw in keywords):
            found_categories.append(cat)
    
    if len(found_categories) == 1:
        category = found_categories[0]
    elif len(found_categories) > 1:
        category = found_categories[0] # Pick first but flag for review
        flag = "NEEDS_REVIEW"
    else:
        flag = "NEEDS_REVIEW" # Ambiguous if no keywords found

    # Identify Priority
    priority = "Standard"
    triggered_keywords = [kw for kw in URGENT_KEYWORDS if kw in description]
    
    if triggered_keywords:
        priority = "Urgent"
        reason = f"Priority set to Urgent because description mentions: {', '.join(triggered_keywords)}."
    else:
        # Default logic for other priorities if needed
        priority = "Standard"
        reason = f"Classified as {category} based on description keywords."

    return {
        "category": category,
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
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            rows_to_write = []
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                    rows_to_write.append(row)
                except Exception as e:
                    print(f"Error classifying row {row.get('id', 'unknown')}: {e}")
                    # Still add the row but with error indicators
                    row.update({"category": "Other", "priority": "Low", "reason": f"Error: {e}", "flag": "NEEDS_REVIEW"})
                    rows_to_write.append(row)

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
