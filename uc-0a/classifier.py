"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"
]
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    comp_id = row.get("complaint_id", "")
    desc = row.get("description", "").lower()
    
    if not desc.strip():
        return {
            "complaint_id": comp_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty or missing.",
            "flag": "NEEDS_REVIEW"
        }

    # Identify category
    found_categories = []
    for cat in CATEGORIES:
        if cat.lower() in desc:
            found_categories.append(cat)
            
    if len(found_categories) == 1:
        category = found_categories[0]
        flag = ""
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Identify priority
    urgent_words_found = [word for word in URGENT_KEYWORDS if word in desc]
    if urgent_words_found:
        priority = "Urgent"
    else:
        priority = "Standard" if category != "Other" else "Low"

    # Generate reason
    if category == "Other" and flag == "NEEDS_REVIEW":
        reason = "Category could not be definitively determined or is ambiguous."
    else:
        reason_word = urgent_words_found[0] if urgent_words_found else category.lower()
        reason = f"Classified based on the presence of '{reason_word}' in the description."

    return {
        "complaint_id": comp_id,
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
            
            with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    try:
                        result = classify_complaint(row)
                        writer.writerow(result)
                    except Exception as e:
                        print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                        # Fallback row per skills.md
                        writer.writerow({
                            "complaint_id": row.get("complaint_id", ""),
                            "category": "Other",
                            "priority": "Low",
                            "reason": f"Processing error: {str(e)}",
                            "flag": "NEEDS_REVIEW"
                        })
    except Exception as e:
        print(f"Failed to process file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
