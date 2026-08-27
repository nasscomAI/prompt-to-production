"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using R.I.C.E enforcement rules.
    Role: Skill 1 - Individual row classification.
    Intent: Accurate category, priority, reason, and flag assignment.
    Context: Input dictionary containing 'description' and 'complaint_id'.
    Enforcement: Strict taxonomy, priority keywords, and mandatory reasons.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Enforcement: Priority Rules
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            break
            
    # 2. Enforcement: Category Taxonomy (Keyword mapping)
    category_map = {
        "Pothole": ["pothole", "pit"],
        "Flooding": ["flood", "waterlog", "inundation"],
        "Streetlight": ["streetlight", "lamp", "dark"],
        "Waste": ["waste", "garbage", "trash", "dump"],
        "Noise": ["noise", "loud", "sound"],
        "Road Damage": ["road", "crack", "pavement"],
        "Heritage Damage": ["heritage", "statue", "monument", "ancient"],
        "Heat Hazard": ["heat", "hot", "sunstroke"],
        "Drain Blockage": ["drain", "sewage", "gutter", "block"]
    }
    
    category = "Other"
    found_keyword = None
    for cat, kws in category_map.items():
        for kw in kws:
            if kw in description:
                category = cat
                found_keyword = kw
                break
        if category != "Other":
            break
            
    # 3. Enforcement: Flag field
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    # 4. Enforcement: Mandatory Reason (citing specific words)
    if category != "Other" and found_keyword:
        reason = f"The complaint mentions '{found_keyword}' which indicates a {category} issue."
    else:
        reason = "The category is genuinely ambiguous and requires manual review."
        
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
    Role: Skill 2 - CSV Orchestration.
    Intent: Verifiable output file even if some rows fail.
    Context: Input and output file paths.
    Enforcement: Schema consistency and null handling.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Context: handle missing values
                    if not row.get("description"):
                        continue
                    
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    
        if not results:
            print("No valid rows to write.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"An unexpected error occurred during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
