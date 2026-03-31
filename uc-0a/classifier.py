"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys

def classify_complaint(row: dict) -> dict:
    description = str(row.get("description", "")).lower()
    
    # Priority classification based on keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    urgent_pattern = re.compile(rf'\b({"|".join(urgent_keywords)})\b', re.IGNORECASE)
    
    priority = "Low"
    reason = ""
    
    match = urgent_pattern.search(description)
    if match:
        priority = "Urgent"
        reason = f"Contains urgent keyword: {match.group(1)}."
    else:
        priority = "Low"  # Default as requested by prompt logic fallback
        reason = "Standard processing."

    # Sub-category classification matching exact enums
    category = "Other"
    flag = "NEEDS_REVIEW"
    
    categories = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water", "burst"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "garbage", "trash"],
        "Noise": ["noise", "loud"],
        "Road Damage": ["road", "crack"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain", "blockage"]
    }
    
    found_categories = []
    for cat, kws in categories.items():
        for kw in kws:
            if re.search(rf'\b{kw}\b', description, re.IGNORECASE):
                found_categories.append(cat)
                break
                
    if len(found_categories) == 1:
        category = found_categories[0]
        flag = ""
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"{reason} Multiple categories found."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"{reason} Unclear category."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading input: {e}")
        return

    results = []
    for r in rows:
        try:
            results.append(classify_complaint(r))
        except Exception as e:
            # Output gracefully
            print(f"Failed to process row: {r}. Error: {e}")
            results.append({
                "complaint_id": r.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Error: {e}",
                "flag": "NEEDS_REVIEW"
            })

    if not results:
        print("No results to write.")
        return

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", default="../data/city-test-files/test_pune.csv", help="Path to test_city.csv")
    parser.add_argument("--output", default="results_pune.csv", help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
