"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the RICE prompt enforcement rules.
    Returns: dict with new classification keys.
    """
    description = row.get('description', '').lower()
    
    # Defaults
    category = "Other"
    priority = "Low"
    reason = "Invalid input or empty description."
    flag = "NEEDS_REVIEW"
    
    if not description or not str(description).strip():
        return {
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }

    # Keyword mapping setup for heuristics
    category_map = {
        "pothole": "Pothole", "crater": "Pothole",
        "flood": "Flooding", "water": "Flooding",
        "streetlight": "Streetlight", "light": "Streetlight", "dark": "Streetlight",
        "waste": "Waste", "garbage": "Waste", "trash": "Waste",
        "noise": "Noise", "loud": "Noise",
        "road": "Road Damage", "crack": "Road Damage",
        "heritage": "Heritage Damage", "monument": "Heritage Damage",
        "heat": "Heat Hazard", "hot": "Heat Hazard",
        "drain": "Drain Blockage", "block": "Drain Blockage", "clog": "Drain Blockage"
    }

    found_categories = set()
    found_keywords = []
    
    for kw, cat in category_map.items():
        if kw in description:
            found_categories.add(cat)
            found_keywords.append(kw)

    if len(found_categories) == 1:
        category = list(found_categories)[0]
        reason = f"The description identifies the issue containing the word '{found_keywords[0]}'."
        flag = ""  # clear
    elif len(found_categories) > 1:
        category = "Other"
        reason = f"The description is ambiguous, mentioning both '{found_keywords[0]}' and '{found_keywords[1]}'."
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        reason = "The description lacks specific identifiable keywords."
        flag = "NEEDS_REVIEW"

    # Enforce priority rule based on severity keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if kw in description]
    
    if found_urgent:
        priority = "Urgent"
        reason = f"The situation is classified as Urgent because it mentions '{found_urgent[0]}'."
    else:
        priority = "Standard" if category != "Other" else "Low"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results to the output CSV.
    """
    results = []
    out_fields = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            out_fields = list(dict.fromkeys(fieldnames + ['category', 'priority', 'reason', 'flag']))
            
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                except Exception as e:
                    print(f"Error classifying row: {e}")
                    row.update({
                        "category": "Other", 
                        "priority": "Low", 
                        "reason": "An error occurred during classification.", 
                        "flag": "NEEDS_REVIEW"
                    })
                results.append(row)
                
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
