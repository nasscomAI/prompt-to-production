"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_MAPPING = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "rain", "stranded"],
    "Streetlight": ["streetlight", "dark", "sparking", "lights out"],
    "Waste": ["garbage", "waste", "dead animal", "smell", "bin"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["cracked", "sinking", "manhole", "footpath", "broken", "upturned"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain blocked", "drainage"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = str(row.get("description", "")).lower()
    
    # Priority Enforcement
    matched_severity = [word for word in SEVERITY_KEYWORDS if word in description]
    priority = "Urgent" if matched_severity else "Standard"

    # Category Enforcement
    matched_cats = []
    matched_words_map = {}
    
    for cat, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if kw in description:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                    matched_words_map[cat] = []
                matched_words_map[cat].append(kw)
    
    # Flag constraints
    if len(matched_cats) > 1:
        category = matched_cats[0]
        flag = "NEEDS_REVIEW"
        reason = f"Category ambiguous. Matched '{matched_words_map[category][0]}'."
    elif len(matched_cats) == 1:
        category = matched_cats[0]
        flag = ""
        reason = f"Categorized based on the keyword '{matched_words_map[category][0]}' found in description."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not identify any specific category keywords in the description."

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
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Error: Input CSV is empty.")
                return
            
            out_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
            
            with open(output_path, "w", encoding="utf-8", newline="") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
                writer.writeheader()
                
                success = 0
                failed = 0
                for row_num, row in enumerate(reader, 1):
                    try:
                        classification = classify_complaint(row)
                        row.update(classification)
                        writer.writerow(row)
                        success += 1
                    except Exception as e:
                        print(f"Row {row_num} failed classification: {e}")
                        failed += 1
                        
                print(f"Processed batch. Success: {success}, Failed: {failed}")
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_path}'.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
