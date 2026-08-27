"""
UC-0A — Complaint Classifier
Implementation based on RICE principles, agents.md, and skills.md.
"""
import argparse
import csv
import re

# Defined strictly from agents.md enforcement rules
ALLOWED_CATEGORIES = {
    "Pothole": [r'pothole', r'crater'],
    "Flooding": [r'flood', r'waterlogging', r'waterlogged', r'submerged'],
    "Streetlight": [r'streetlight', r'light\b', r'lights out', r'dark\b', r'sparking'],
    "Waste": [r'garbage', r'waste', r'trash', r'dump', r'smell', r'dead animal'],
    "Noise": [r'noise', r'loud', r'music', r'dj', r'speaker'],
    "Road Damage": [r'road surface', r'crack', r'sinking', r'manhole', r'tiles broken', r'footpath tiles'],
    "Heritage Damage": [r'heritage', r'monument', r'statue'],
    "Heat Hazard": [r'heat\b', r'temperature', r'sunstroke'],
    "Drain Blockage": [r'drain\b', r'sewer', r'clog', r'drain block\w*']
}

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint row into a strict schema.
    Returns: dict with updated keys including category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Check severity
    priority = "Standard"
    matched_severity_kw = None
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            matched_severity_kw = kw
            break  # First matched severity is enough
            
    # Check category
    matched_cats = {}
    for cat, regex_list in ALLOWED_CATEGORIES.items():
        for pattern in regex_list:
            match = re.search(pattern, description)
            if match:
                if cat not in matched_cats:
                    matched_cats[cat] = []
                # Keep the matched word to cite in reason
                matched_cats[cat].append(match.group())

    category = "Other"
    reason = ""
    flag = ""
    
    unique_matched_cats = list(matched_cats.keys())
    
    if len(unique_matched_cats) == 1:
        category = unique_matched_cats[0]
        cited_word = matched_cats[category][0]
        if priority == "Urgent":
            reason = f"The description contains '{cited_word}' indicating {category}, and is marked Urgent because it contains '{matched_severity_kw}'."
        else:
            reason = f"The description is classified as {category} because it mentions the specific word '{cited_word}'."
    elif len(unique_matched_cats) > 1:
        # Genuinely ambiguous as per rule 4
        category = "Other"
        flag = "NEEDS_REVIEW"
        conflict_words = [matched_cats[c][0] for c in unique_matched_cats[:2]]
        reason = f"The description is genuinely ambiguous as it contains multiple conflicting keywords like '{conflict_words[0]}' and '{conflict_words[1]}'."
    else:
        # No known categories matched
        category = "Other"
        flag = "NEEDS_REVIEW"
        if priority == "Urgent":
            reason = f"No specific category words were found, but it is Urgent due to '{matched_severity_kw}'."
        else:
            reason = "The description does not clearly align with any predefined categories, requiring manual review."

    # Update row safely
    result = dict(row)
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, and produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames)
            
            # Ensure output columns exist
            for target_field in ['category', 'priority', 'reason', 'flag']:
                if target_field not in fieldnames:
                    fieldnames.append(target_field)
            
            classified_rows = []
            row_count = 0
            for idx, row in enumerate(reader, start=1):
                row_count += 1
                try:
                    # Skip completely empty rows
                    if not any(row.values()):
                        print(f"Skipping empty row at line {idx + 1}")
                        continue
                        
                    result_row = classify_complaint(row)
                    classified_rows.append(result_row)
                except Exception as e:
                    print(f"Failed to process row {idx + 1}: {e}")
                    # In accordance to skills.md error handling: skip malformed rows, log it.

        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(classified_rows)
            
    except Exception as e:
        print(f"Critical error processing batch classify: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
