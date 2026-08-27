"""
UC-0A — Complaint Classifier
Implementation based on RICE (agents.md) and skills.md.
"""
import argparse
import csv
import os

# Configuration from agents.md / README.md
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "dip in road", "road hole", "pitting"],
    "Flooding": ["flood", "waterlogging", "rain water", "submerged", "stagnant water"],
    "Streetlight": ["streetlight", "light out", "dark at night", "lamp", "flickering"],
    "Waste": ["waste", "garbage", "trash", "dump", "smell", "litter", "debris", "dead animal"],
    "Noise": ["noise", "loud", "music", "construction sound", "honking", "shouting"],
    "Road Damage": ["road damage", "crack", "uneven road", "asphalt", "manhole", "footpath", "tiles", "pavement"],
    "Heritage Damage": ["heritage", "monument", "historic", "ancient structure", "heritage street"],
    "Heat Hazard": ["heat", "sunstroke", "hot weather", "cooling", "burning"],
    "Drain Blockage": ["drain", "sewage", "gutter", "blockage", "overflow", "sewer"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = str(row.get("description", "")).lower()
    
    # 1. Determine Category
    matched_category = "Other"
    found_keywords = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                matched_category = category
                found_keywords.append(kw)
                break
        if matched_category != "Other":
            break

    # 2. Determine Priority
    priority = "Standard"
    severity_found = []
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            severity_found.append(kw)
    
    # 3. Determine Flag
    flag = ""
    if matched_category == "Other" or not description.strip():
        flag = "NEEDS_REVIEW"
        
    # 4. Generate Reason (One sentence citing specific words)
    if matched_category != "Other":
        reason = f"Classified as {matched_category} because the description mentions '{found_keywords[0]}'."
    elif description.strip():
        reason = "Category could not be determined from the description alone."
    else:
        reason = "Description is missing or empty."
        
    if priority == "Urgent":
        reason += f" Priority set to Urgent due to keyword '{severity_found[0]}'."
    
    return {
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    headers = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            for row in reader:
                # Basic null handling
                if not row:
                    continue
                
                classification = classify_complaint(row)
                
                # Combine original row with classification (if columns don't overlap)
                # But README says category and priority_flag columns are stripped — we must add them.
                # Common headers in input: description, complaint_id (assumed)
                output_row = row.copy()
                output_row.update(classification)
                results.append(output_row)
                
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    if not results:
        print("No data processed.")
        return

    # Prepare output headers
    # Ensure category, priority, reason, flag are included
    out_headers = list(results[0].keys())
    
    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_headers)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
