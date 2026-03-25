"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # Priority Keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    if any(word in description for word in severity_keywords):
        priority = "Urgent"
    
    # Category Keywords mapping
    category_map = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogged", "water accumulation", "submerged"],
        "Streetlight": ["streetlight", "street light", "lamp", "lights out", "dark at night"],
        "Waste": ["garbage", "trash", "waste", "bins", "smell", "dumped", "dead animal"],
        "Noise": ["noise", "loud", "music", "sound", "volume"],
        "Road Damage": ["road surface", "cracked", "sinking", "footpath", "tiles broken", "pavement"],
        "Heritage Damage": ["heritage", "monument", "historic"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "dehydration"],
        "Drain Blockage": ["drain", "sewage", "gutter", "overflow"],
    }
    
    category = "Other"
    flag = ""
    
    # Simple matching logic
    matched_categories = []
    for cat, keywords in category_map.items():
        if any(kw in description for kw in keywords):
            matched_categories.append(cat)
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        # If multiple categories match, pick the most specific one or mark for review
        # For simplicity, we'll pick the first and flag it
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    elif not description:
        category = "Other"
        flag = "NEEDS_REVIEW"
    
    # Reasoning
    reason = "Classification based on keywords in description."
    found_keywords = [word for word in (severity_keywords + [kw for kws in category_map.values() for kw in kws]) if word in description]
    if found_keywords:
        reason = f"Identified '{found_keywords[0]}' in description, suggesting {category} and {priority} priority."
    
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
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Log error and provide a fallback row to avoid missing data
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
        
        if not results:
            print(f"No data found in {input_path}")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
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
