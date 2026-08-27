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
    complaint_id = row.get("complaint_id", "")
    description = str(row.get("description", "")).strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    
    # Priority Evaluation
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if kw in desc_lower]
    
    if found_urgent:
        priority = "Urgent"
        priority_reason = f"priority Urgent because it mentions '{found_urgent[0]}'"
    else:
        priority = "Standard"
        priority_reason = "Standard priority"

    # Category Evaluation
    categories_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging", "water logging"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "garbage", "trash", "dead animal", "dump"],
        "Noise": ["noise", "loud", "music", "speaker"],
        "Road Damage": ["road", "crack", "broken", "footpath"],
        "Heritage Damage": ["heritage", "monument", "statue"],
        "Heat Hazard": ["heat", "sun", "hot"],
        "Drain Blockage": ["drain", "block", "clog", "sewer", "manhole"]
    }
    
    category = "Other"
    flag = "NEEDS_REVIEW"
    cat_cited_word = ""
    
    for cat, keywords in categories_map.items():
        found_cat_kw = [kw for kw in keywords if kw in desc_lower]
        if found_cat_kw:
            category = cat
            flag = ""  # Clear flag if category found
            cat_cited_word = found_cat_kw[0]
            break

    if category != "Other":
        reason = f"Classified as {category} due to the word '{cat_cited_word}' and {priority_reason}."
    else:
        # Fallback reason if ambiguous
        first_word = description.split()[0] if description else ""
        reason = f"Ambiguous category (contains '{first_word}'), assigned Other and {priority_reason}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
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
                    results.append({
                        "complaint_id": row.get("complaint_id", "unknown"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return

    if not results:
        print("No data to process.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
    except Exception as e:
        print(f"Error writing output: {str(e)}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
