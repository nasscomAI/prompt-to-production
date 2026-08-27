"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = str(row.get('description', '')).lower()
    
    # Determine Category
    matched_categories = []
    if "pothole" in description:
        matched_categories.append("Pothole")
    if "flood" in description or "waterlogging" in description:
        matched_categories.append("Flooding")
    if "light" in description:
        matched_categories.append("Streetlight")
    if "waste" in description or "garbage" in description or "trash" in description:
        matched_categories.append("Waste")
    if "noise" in description or "loud" in description:
        matched_categories.append("Noise")
    if "road damage" in description or "cracks" in description:
        matched_categories.append("Road Damage")
    if "heritage" in description or "monument" in description:
        matched_categories.append("Heritage Damage")
    if "heat" in description:
        matched_categories.append("Heat Hazard")
    if "drain" in description:
        matched_categories.append("Drain Blockage")
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Determine Priority
    urgent_words_found = []
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', description):
            urgent_words_found.append(keyword)
            
    if urgent_words_found:
        priority = "Urgent"
        reason = f"Severity keyword '{urgent_words_found[0]}' found in description."
    else:
        priority = "Standard"
        words = description.split()
        snippet_words = [words[i] for i in range(min(5, len(words)))]
        snippet = " ".join(snippet_words) + "..." if len(words) > 5 else description
        reason = f"Classified based on keywords: '{snippet}'"
        
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
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
        fields = reader.fieldnames
        final_fields = list(fields) if fields else []
        for f in ['category', 'priority', 'reason', 'flag']:
            final_fields.append(f)
        final_fields = list(dict.fromkeys(final_fields))
        
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=final_fields)
        writer.writeheader()
        
        for row in rows:
            try:
                classification = classify_complaint(row)
                row.update(classification)
                writer.writerow(row)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                row['flag'] = "NEEDS_REVIEW"
                writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
