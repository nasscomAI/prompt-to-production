"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Configuration based on agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Simple keyword mapping for categories
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "water", "submerged", "rain"],
    "Streetlight": ["streetlight", "light", "dark", "lamp"],
    "Waste": ["garbage", "trash", "waste", "dump", "animal", "bin"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["road surface", "cracked", "sinking", "manhole", "footpath", "tiles", "broken"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "sun", "temperature", "hot"],
    "Drain Blockage": ["drain blocked", "drainage", "clogged drain"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty description provided.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Category
    matched_categories = []
    reason_word = ""
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                matched_categories.append(cat)
                reason_word = kw
                break # Move to next category if one keyword matches
    
    # Enforcement: Exact strings only, flag if ambiguous
    category = "Other"
    flag = ""
    
    if len(set(matched_categories)) == 1:
        category = matched_categories[0]
    elif len(set(matched_categories)) > 1:
        category = matched_categories[0] # Pick the first match
        flag = "NEEDS_REVIEW" # Ambiguous
    else:
        category = "Other"
        if not reason_word:
            flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    priority = "Standard"
    severity_match = ""
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            severity_match = kw
            break
    
    # 3. Construct Reason (Must cite specific words)
    if severity_match:
        reason = f"Urgent priority due to keyword '{severity_match}'. Category '{category}' identified via '{reason_word or 'context'}'. "
    elif reason_word:
        reason = f"Classified as {category} based on the word '{reason_word}' in the description."
    else:
        reason = "Category could not be definitively determined from description keywords."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles nulls and avoids crashing on bad rows.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Basic validation: check if row is empty
                    if not any(row.values()):
                        continue
                    
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                    # Ensure we still produce output even if a row fails
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

        # Write results
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print(f"Critical error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
