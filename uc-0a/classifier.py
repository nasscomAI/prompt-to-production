"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based keyword matching.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # Priority classification
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Urgent" if any(kw in description for kw in urgent_keywords) else "Standard"
    
    # Category classification using keyword mapping
    category_map = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogging", "submerged"],
        "Streetlight": ["streetlight", "street light", "lamp", "darkness"],
        "Waste": ["garbage", "trash", "waste", "dumping", "refuse"],
        "Noise": ["loud", "noise", "music", "blaring"],
        "Road Damage": ["road crack", "pavement", "collapsed road", "road repair"],
        "Heritage Damage": ["statue", "monument", "historic", "heritage", "ancient"],
        "Heat Hazard": ["heat", "extreme temperature", "sunstroke", "burning"],
        "Drain Blockage": ["drain", "sewer", "clogged", "drainage"],
    }
    
    found_categories = []
    for cat, keywords in category_map.items():
        if any(kw in description for kw in keywords):
            found_categories.append(cat)
    
    # RICE Enforcement: One category only or flag NEEDS_REVIEW
    category = "Other"
    flag = ""
    reason = ""
    
    if len(found_categories) == 1:
        category = found_categories[0]
        # Cite specific words for reason
        matched_kw = [kw for kw in category_map[category] if kw in description][0]
        reason = f"Classification based on presence of the word '{matched_kw}' indicating a {category.lower()} issue."
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous description matched multiple categories: {', '.join(found_categories)}."
    elif not description:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Empty description provided."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not determine a specific category from the description."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write the output CSV.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    results.append(classify_complaint(row))
                except Exception as e:
                    # Not crashing on bad rows, flagging them
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
        
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Fatal error during batch classification: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
