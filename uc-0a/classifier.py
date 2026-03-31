"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Priority classification
    urgent_words_found = [w for w in URGENT_KEYWORDS if w in description]
    priority = "Urgent" if urgent_words_found else "Standard"
    
    # Category and Reason Logic
    found_categories = []
    category_keywords = {
        "Pothole": ["pothole", "crater", "hole"],
        "Flooding": ["flood", "waterlogging", "submerged", "water"],
        "Streetlight": ["light", "lamp", "streetlight", "dark"],
        "Waste": ["waste", "garbage", "trash", "dump", "smell"],
        "Noise": ["noise", "loud", "music", "speaker"],
        "Road Damage": ["road damage", "crack", "broken road", "surface"],
        "Heritage Damage": ["heritage", "monument", "statue", "ruin"],
        "Heat Hazard": ["heat", "sun", "temperature", "wave"],
        "Drain Blockage": ["drain", "clog", "blockage", "sewage", "overflow"]
    }
    
    matched_words = []
    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in description:
                if cat not in found_categories:
                    found_categories.append(cat)
                matched_words.append(kw)
                
    flag = ""
    if len(found_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_text = "No specific category keywords found."
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        unique_words = []
        for w in matched_words:
            if w not in unique_words:
                unique_words.append(w)
        snippet = ", ".join(unique_words[:3])
        reason_text = f"Multiple conflicting categories detected based on keywords: {snippet}."
    else:
        category = found_categories[0]
        unique_words = []
        for w in matched_words:
            if w not in unique_words:
                unique_words.append(w)
        snippet = ", ".join(unique_words[:3])
        reason_text = f"Classified as {category} due to mentions of {snippet}."
        
    if urgent_words_found:
        reason_text += f" Priority escalated to Urgent because description contains: {', '.join(urgent_words_found)}."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason_text,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    all_fieldnames = set()
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                    results.append(row)
                    all_fieldnames.update(row.keys())
                except Exception as e:
                    print(f"Skipping bad row: {e}")
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        return

    # Keep output format structured as expected
    out_keys = ["complaint_id", "category", "priority", "reason", "flag"]
    for key in out_keys:
        if key in all_fieldnames:
            all_fieldnames.remove(key)
    
    final_fields = out_keys + list(all_fieldnames)

    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=final_fields)
        writer.writeheader()
        for r in results:
            writer.writerow(r)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
