import argparse
import csv
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def classify_complaint(row: dict) -> dict:
    description = str(row.get("description", "")).lower().strip()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty or missing.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            break
            
    # 2. Determine category
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "dark", "lights out"],
        "Waste": ["garbage", "waste", "smell", "dead animal"],
        "Noise": ["music", "noise"],
        "Road Damage": ["cracked", "manhole", "footpath", "broken", "road surface"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain block"]
    }
    
    matched_categories = []
    reason_kw = None
    for cat, kws in category_keywords.items():
        for kw in kws:
            if kw in description:
                matched_categories.append(cat)
                if not reason_kw:
                    reason_kw = kw
                break # count each category once
    
    # Check for ambiguity
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
        reason = f"The description contains '{reason_kw}' indicating {category}."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"The description contains multiple conflicting keywords: {', '.join(matched_categories)}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No matching keywords were found for any predefined category."
        
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    fieldnames = ["complaint_id", "date_raised", "city", "ward", "location", "description", "reported_by", "days_open", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except Exception as e:
        logging.error(f"Failed to read input file: {str(e)}")
        return

    results = []
    for i, row in enumerate(rows):
        try:
            classification = classify_complaint(row)
            row["category"] = classification.get("category", "")
            row["priority"] = classification.get("priority", "")
            row["reason"] = classification.get("reason", "")
            row["flag"] = classification.get("flag", "")
            # Ensure only standard fields
            clean_row = {
                "complaint_id": row.get("complaint_id"),
                "date_raised": row.get("date_raised"),
                "city": row.get("city"),
                "ward": row.get("ward"),
                "location": row.get("location"),
                "description": row.get("description"),
                "reported_by": row.get("reported_by"),
                "days_open": row.get("days_open"),
                "category": row.get("category"),
                "priority": row.get("priority"),
                "reason": row.get("reason"),
                "flag": row.get("flag"),
            }
            results.append(clean_row)
        except Exception as e:
            logging.error(f"Row {i} failed processing: {str(e)}")
            
    try:
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        logging.error(f"Failed to write output file: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    logging.info(f"Done. Results written to {args.output}")
