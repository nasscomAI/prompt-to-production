"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md requirements.
"""
import argparse
import csv
import re

# Allowed Categories
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity Keywords for Urgent Priority
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Simple Keyword Mapping for Categories
CATEGORY_MAPPING = {
    "Pothole": ["pothole", "crater", "hole in the road"],
    "Flooding": ["flood", "waterlog", "submerge", "overflow", "rain water"],
    "Streetlight": ["streetlight", "street light", "lamp", "bulb", "darkness"],
    "Waste": ["waste", "garbage", "trash", "litter", "dump", "refuse"],
    "Noise": ["noise", "loud", "sound", "music", "construction noise"],
    "Road Damage": ["road damage", "crack", "pavement", "asphalt", "sidewalk"],
    "Heritage Damage": ["heritage", "monument", "statue", "historic", "ancient"],
    "Heat Hazard": ["heat", "hot", "temperature", "sunstroke", "exhaustion"],
    "Drain Blockage": ["drain", "sewer", "clog", "blockage", "gutter"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Priority
    priority = "Standard"
    found_urgent_keywords = [word for word in URGENT_KEYWORDS if word in description]
    if found_urgent_keywords:
        priority = "Urgent"
    else:
        # Heuristic for Low: simple maintenance without urgency
        if any(word in description for word in ["clean", "routine", "paint"]):
            priority = "Low"

    # 2. Determine Category
    matched_categories = []
    found_words = []
    
    for category, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if kw in description:
                matched_categories.append(category)
                found_words.append(kw)
                break
    
    # 3. Handle Ambiguity
    category = "Other"
    flag = ""
    reason_cite = ""
    
    if len(set(matched_categories)) == 1:
        category = matched_categories[0]
        reason_cite = f"Classified as {category} because description mentions '{found_words[0]}'."
    elif len(set(matched_categories)) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = f"Ambiguous: matched multiple categories ({', '.join(set(matched_categories))})."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = "No specific category keywords found in the description."

    # Override priority reason if Urgent
    if priority == "Urgent":
        reason_cite += f" Priority set to Urgent due to keyword: '{found_urgent_keywords[0]}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason_cite,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Continue processing if a single row fails
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    results.append({
                        "complaint_id": row.get('complaint_id', 'ERR'),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Internal error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
        
        if not results:
            print("No results to write.")
            return

        keys = results[0].keys()
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Batch processing failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
