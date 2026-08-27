import argparse
import csv
import os
import re

# Exact taxonomy according to UC-0A
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", 
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that must trigger Urgent
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Skill definition from skills.md: Categorizes one citizen complaint and assigns 
    priority, justification, and an ambiguity flag based on urban maintenance schema.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")

    # 1. Enforcement: Priority Check (Severity Keywords)
    priority = "Standard"
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            break
    
    # 2. Enforcement: Category Logic (Rule-based mapping for demo)
    category = "Other"
    keywords_map = {
        "Pothole": ["pothole", "pit"],
        "Flooding": ["flooding", "flooded", "water", "rain"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "trash", "garbage", "bins", "dumped"],
        "Noise": ["noise", "music", "wedding"],
        "Road Damage": ["cracked", "sinking", "surface", "road", "tiles", "broken"],
        "Drain Blockage": ["drain", "blocked"],
        "Heritage Damage": ["heritage", "old city"]
    }

    # Match category based on keywords
    found_categories = []
    for cat, kws in keywords_map.items():
        if any(kw in description for kw in kws):
            found_categories.append(cat)
    
    if len(found_categories) == 1:
        category = found_categories[0]
    elif len(found_categories) > 1:
        category = found_categories[0] # Take first for now, but flag it

    # 3. Enforcement: Flag Check (Ambiguity)
    flag = ""
    # Flag if genuinely ambiguous or multiple matches
    if len(found_categories) != 1 or len(description) < 20:
        flag = "NEEDS_REVIEW"

    # 4. Enforcement: Reason (One sentence, cite specific words)
    # Extracts the part of the sentence containing the keyword for justification
    justification_word = "Unknown"
    for kw in URGENT_KEYWORDS + sum(keywords_map.values(), []):
        if kw in description:
            justification_word = kw
            break
            
    reason = f"Classified as {category} because description mentions '{justification_word}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Skill definition from skills.md: Reads input CSV, applies classify_complaint per row, 
    and writes results to city-specific output CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # Skill Error Handling: Validate presence of description
                if not row.get("description"):
                    row["flag"] = "NEEDS_REVIEW"
                    row["reason"] = "Missing justification: No description found."
                    results.append(row)
                    continue

                classification = classify_complaint(row)
                # Merge classification with original row
                row.update(classification)
                results.append(row)

        if not results:
            print("No data processed.")
            return

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        fieldnames = results[0].keys()
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        # Skill Error Handling: Mitigate drift and handle corrupted data
        print(f"Error during batch processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Batch processing complete. Results written to: {args.output}")
