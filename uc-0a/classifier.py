"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Enforcement constants from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Keyword mappings for categories (based on common associations)
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole", "crater", "dip"],
    "Flooding": ["flood", "water", "overflow", "rain"],
    "Streetlight": ["streetlight", "light", "bulb", "lamp", "street light"],
    "Waste": ["waste", "garbage", "trash", "dump", "rubbish"],
    "Noise": ["noise", "loud", "sound", "music", "party"],
    "Road Damage": ["road", "damage", "crack", "pavement", "asphalt"],
    "Heritage Damage": ["heritage", "monument", "historical", "statue", "building"],
    "Heat Hazard": ["heat", "hot", "temperature", "sun", "scorching"],
    "Drain Blockage": ["drain", "block", "clog", "sewer", "pipe"],
    "Other": []
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Guided by agents.md and skills.md.
    """
    description = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', '')
    
    # Determine category based on keywords
    matches = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "Other":
            continue
        if any(keyword in description for keyword in keywords):
            matches.append(category)
    
    if len(matches) == 1:
        category = matches[0]
        flag = ""
        reason = f"Classified as {category} because the description contains '{matches[0]}'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Category is ambiguous or not determinable from the description alone."
    
    # Determine priority
    if any(keyword in description for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"  # Default to Standard if not Urgent
    
    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Guided by skills.md.
    Handles file I/O errors, processes all rows even if some fail.
    """
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file {input_path} not found.")
    except Exception as e:
        raise Exception(f"Error reading input file: {e}")
    
    results = []
    for row in rows:
        try:
            classified = classify_complaint(row)
            # Merge original row with classified fields
            result_row = {**row, **classified}
            results.append(result_row)
        except Exception as e:
            # If classification fails, still include row with error flag
            result_row = {**row, 'category': 'Other', 'priority': 'Standard', 'reason': f'Classification failed: {e}', 'flag': 'NEEDS_REVIEW'}
            results.append(result_row)
    
    if results:
        fieldnames = list(results[0].keys())
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            raise Exception(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
