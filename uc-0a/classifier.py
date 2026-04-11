"""
UC-0A — Complaint Classifier
Implemented based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", 
    "ambulance", "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAPPING = {
    "Pothole": ["pothole", "crater", "potholes"],
    "Flooding": ["flood", "waterlog", "submerge", "flooding"],
    "Streetlight": ["streetlight", "street light", "dark", "lamp"],
    "Waste": ["waste", "garbage", "trash", "dump"],
    "Noise": ["noise", "loud", "music", "speaker"],
    "Road Damage": ["crack", "road", "broken road", "damage"],
    "Heritage Damage": ["heritage", "monument", "statue", "historical"],
    "Heat Hazard": ["heat", "hot", "sunburn"],
    "Drain Blockage": ["drain", "clog", "sewer", "sewage"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get("description", "")).lower()
    complaint_id = row.get("complaint_id", "")
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Category
    matched_category = "Other"
    matched_words = []
    
    for cat, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc):
                matched_category = cat
                matched_words.append(kw)
                break
        if matched_category != "Other":
            break
            
    # Ambiguity check
    flag = ""
    if matched_category == "Other":
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    priority = "Standard"
    found_severity_keywords = []
    for skw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(skw) + r'\b', desc):
            found_severity_keywords.append(skw)
    
    if found_severity_keywords:
        priority = "Urgent"

    # 3. Create Reason Statement
    reason_words = matched_words + found_severity_keywords
    if reason_words:
        citing = ', '.join(f"'{w}'" for w in set(reason_words))
        reason = f"Classified based on explicit mention of {citing}."
    else:
        reason = "Could not identify specific keywords for classification."

    return {
        "complaint_id": complaint_id,
        "category": matched_category,
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
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            results = []
            
            for row in reader:
                try:
                    res = classify_complaint(row)
                except Exception as e:
                    # Fallback on crash
                    res = {
                        "complaint_id": row.get("complaint_id", "unknown"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    }
                results.append(res)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Error processing batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
