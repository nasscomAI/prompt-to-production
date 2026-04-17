"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    
    # 1. Determine Priority based on severity keywords
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = any(kw in description for kw in severity_keywords)
    priority = "Urgent" if is_urgent else "Standard"

    # 2. Determine Category based on text matching
    category = "Other"
    flag = "NEEDS_REVIEW"
    reason = "Could not determine category from description."

    if 'pothole' in description:
        category = "Pothole"
        flag = ""
        reason = "Description mentions 'pothole'."
    elif 'drain' in description and 'block' in description:
        category = "Drain Blockage"
        flag = ""
        reason = "Description mentions 'drain blocked'."
    elif 'flood' in description:
        category = "Flooding"
        flag = ""
        reason = "Description mentions 'flooded' or 'floods'."
    elif 'light' in description or 'dark' in description:
        category = "Streetlight"
        flag = ""
        reason = "Description mentions 'lights' or 'dark'."
    elif 'garbage' in description or 'waste' in description or 'dead animal' in description:
        category = "Waste"
        flag = ""
        reason = "Description mentions 'garbage', 'waste', or 'animal'."
    elif 'music' in description or 'noise' in description:
        category = "Noise"
        flag = ""
        reason = "Description mentions 'music' or 'noise'."
    elif 'crack' in description or 'sink' in description or 'manhole' in description or 'broken' in description or 'upturned' in description:
        category = "Road Damage"
        flag = ""
        reason = "Description mentions 'cracked', 'broken', or 'manhole'."
    
    # 3. Build and return result
    row_out = row.copy()
    row_out['category'] = category
    row_out['priority'] = priority
    row_out['reason'] = reason
    row_out['flag'] = flag
    
    return row_out


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    if not rows:
        print("Warning: Input CSV is empty.")
        return

    # Prepare output headers (original + new classified fields)
    fieldnames = list(rows[0].keys())
    for new_col in ['category', 'priority', 'reason', 'flag']:
        if new_col not in fieldnames:
            fieldnames.append(new_col)
            
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            try:
                classified_row = classify_complaint(row)
                writer.writerow(classified_row)
            except Exception as e:
                # Error handling for malformed rows
                row['category'] = 'Other'
                row['priority'] = 'Standard'
                row['reason'] = f"Classification error: {str(e)}"
                row['flag'] = 'NEEDS_REVIEW'
                writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
