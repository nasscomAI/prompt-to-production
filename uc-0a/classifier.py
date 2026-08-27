"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAP = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "water"],
    "Streetlight": ["streetlight", "light", "dark"],
    "Waste": ["garbage", "waste", "dump", "animal", "smell"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["road", "crack", "sinking", "surface", "footpath", "tile"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain", "manhole"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Category Classification
    category = "Other"
    flag = "NEEDS_REVIEW"
    cat_word_used = None
    
    for cat, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw in desc:
                if not cat_word_used:
                    category = cat
                    flag = ""
                    cat_word_used = kw
                break
        if cat_word_used:
            break

    # Priority Classification
    priority = "Standard"
    sev_word_used = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            sev_word_used = kw
            break
            
    # Reason formulation
    if cat_word_used and sev_word_used:
        reason = f"Category determined by '{cat_word_used}' and priority is Urgent due to '{sev_word_used}'."
    elif cat_word_used:
        reason = f"Category determined by the presence of the word '{cat_word_used}'."
    elif sev_word_used:
        reason = f"Category is ambiguous, but priority is Urgent due to '{sev_word_used}'."
    else:
        reason = "Category cannot be determined from description alone."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read {input_path}: {e}")
        sys.exit(1)
        
    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write {output_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
