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
    description = str(row.get('description', '')).lower()
    complaint_id = row.get('complaint_id', '')
    
    category = "Other"
    priority = "Standard"
    reason = "No specific keywords found."
    flag = ""
    
    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty description.",
            "flag": "NEEDS_REVIEW"
        }
    
    categories_map = {
        "Pothole": ["pothole", "crater", "potholes"],
        "Flooding": ["flood", "waterlog", "waterlogged", "water logging"],
        "Streetlight": ["streetlight", "street light", "dark street", "no light"],
        "Waste": ["garbage", "trash", "waste", "rubbish", "dump"],
        "Noise": ["noise", "loud music", "loud"],
        "Road Damage": ["crack", "road damage", "broken road", "broken street"],
        "Heritage Damage": ["heritage", "monument", "statue"],
        "Heat Hazard": ["heat", "heatwave", "excessive heat"],
        "Drain Blockage": ["drain", "clogged", "sewer", "blockage"]
    }
    
    found_categories = []
    matched_cat_keywords = []
    for cat, keywords in categories_map.items():
        matched_kws = [kw for kw in keywords if kw in description]
        if matched_kws:
            found_categories.append(cat)
            matched_cat_keywords.extend(matched_kws)
            
    if len(found_categories) == 1:
        category = found_categories[0]
        reason = f"Identified category keywords: {', '.join(matched_cat_keywords)}."
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Multiple categories identified based on keywords: {', '.join(matched_cat_keywords)}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Category cannot be determined from description."

    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_severities = [kw for kw in severity_keywords if kw in description]
    
    if found_severities:
        priority = "Urgent"
        reason += f" Priority set to Urgent due to severity keywords: {', '.join(found_severities)}."
    elif category == "Other":
        priority = "Low"
        
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
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    try:
                        result = classify_complaint(row)
                        writer.writerow(result)
                    except Exception as e:
                        writer.writerow({
                            "complaint_id": row.get('complaint_id', 'UNKNOWN'),
                            "category": "Other",
                            "priority": "Low",
                            "reason": f"Error processing row: {str(e)}",
                            "flag": "NEEDS_REVIEW"
                        })
    except Exception as e:
        print(f"Failed to process files: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
