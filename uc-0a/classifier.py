import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row with strict enforcement of agents.md rules.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")
    
    # 1. Handle missing/null descriptions (Strict enforcement)
    if not description or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = description.lower()
    
    # 2. Priority check (Safety keywords)
    safety_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_safety = [kw for kw in safety_keywords if kw in desc_lower]
    priority = "Urgent" if found_safety else "Standard"
    
    # 3. Category taxonomy mapping
    taxonomy = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["light", "dark", "streetlamp"],
        "Waste": ["garbage", "waste", "dumped", "dead animal", "smell"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["cracked", "sinking", "footpath", "tiles broken", "manhole"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "sunstroke"],
        "Drain Blockage": ["drain", "sewage"],
    }
    
    category = "Other"
    match_keyword = None
    matches = []
    
    for cat, keywords in taxonomy.items():
        for kw in keywords:
            if kw in desc_lower:
                matches.append((cat, kw))
                break
    
    if len(matches) == 1:
        category, match_keyword = matches[0]
    elif len(matches) > 1:
        # Ambiguous case: pick the first but require review
        category, match_keyword = matches[0]
    
    # 4. Reason construction (Must cite specific words)
    if match_keyword:
        reason = f"Classified as {category} because description mentions '{match_keyword}'."
    else:
        reason = "No specific category keywords found."

    if found_safety:
        reason += f" Priority set to Urgent due to: '{found_safety[0]}'."
    
    # 5. Flag logic
    flag = ""
    if category == "Other" or len(matches) > 1 or not match_keyword:
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, process rows, and ensure the script doesn't crash on bad data.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                try:
                    # Skip completely empty rows
                    if not row or not any(row.values()):
                        continue
                    results.append(classify_complaint(row))
                except Exception as row_error:
                    print(f"Skipping row {i+1} due to error: {row_error}")
                    continue
    except Exception as e:
        print(f"Critical error reading CSV: {e}")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
