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
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # Category mapping
    categories = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogging", "rain water"],
        "Streetlight": ["streetlight", "street light", "lamp", "dark"],
        "Waste": ["garbage", "trash", "waste", "dump", "litter"],
        "Noise": ["noise", "loud", "sound"],
        "Road Damage": ["road", "crack", "surface", "tile"],
        "Heritage Damage": ["heritage", "monument", "statue", "temple", "history"],
        "Heat Hazard": ["heat", "hot", "sun", "exhaustion"],
        "Drain Blockage": ["drain", "blockage", "sewage", "gutter"]
    }

    category = "Other"
    matched_word = ""
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in description:
                category = cat
                matched_word = kw
                break
        if category != "Other":
            break

    # Priority logic
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            if not matched_word: # prioritize severity for citation if no category match
                matched_word = kw
            break
            
    # Reason and Flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = f"Category could not be determined from the description."
    else:
        # Cited reason
        cited_word = matched_word if matched_word else "details"
        reason = f"Classified as {category} because the description mentions {cited_word}."

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
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    result = classify_complaint(row)
                    writer.writerow(result)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
