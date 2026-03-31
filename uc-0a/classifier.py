"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Determine Priority
    urgency_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    matched_urgency_words = [word for word in urgency_keywords if word in description]
    if matched_urgency_words:
        priority = "Urgent"

    # Determine Category
    category_map = {
        "Pothole": ["pothole"],
        "Drain Blockage": ["drain block", "drain"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["garbage", "waste", "animal", "dump"],
        "Noise": ["music", "noise"],
        "Road Damage": ["road surface", "manhole", "footpath", "crack"],
        "Heritage Damage": ["heritage damage", "monument"],
        "Heat Hazard": ["heat", "sunstroke"]
    }
    
    category = "Other"
    flag = "NEEDS_REVIEW"
    matched_cat_words = []
    
    for cat, keywords in category_map.items():
        matched = [kw for kw in keywords if kw in description]
        if matched:
            category = cat
            flag = ""
            matched_cat_words.extend(matched)
            break # just take the first matched category
            
    # Compile Reason
    reason_words = matched_urgency_words + matched_cat_words
    if not reason_words:
        reason = "Could not confidently classify from description alone."
    else:
        reason = f"Description contains specific keywords: {', '.join(set(reason_words))}."

    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
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
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
