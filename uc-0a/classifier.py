"""
UC-0A — Complaint Classifier
Implementation using keyword matching.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()
    
    # Priority check
    urgent_keywords = ["injury", "child", "school", "hospital", "danger", "emergency", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if kw in description]
    
    if found_urgent:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # Category check
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "light", "dark", "spark"],
        "Waste": ["waste", "garbage", "trash", "dump", "dead animal"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["crack", "sinking", "broken", "road surface"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain", "manhole"],
        "Other": ["graffiti"]
    }
    
    matched_cats = set()
    reasons = []
    
    for cat, kws in category_keywords.items():
        found = [kw for kw in kws if kw in description]
        if found:
            matched_cats.add(cat)
            reasons.extend(found)
            
    if len(matched_cats) == 1:
        category = matched_cats.pop()
        flag = ""
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    all_reasons = found_urgent + reasons
    if all_reasons:
        selected_reasons = list(set(all_reasons))
        reason = f"Keywords detected: {', '.join(selected_reasons)}."
    else:
        reason = "Could not determine exact category from description keywords."
        
    return {
        "complaint_id": row.get("complaint_id", "unknown"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    results.append(classify_complaint(row))
                except Exception as e:
                    print(f"Error classifying row {row}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "unknown"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    try:
        output_keys = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=output_keys)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
