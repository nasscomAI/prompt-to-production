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
    description = str(row.get("description", "")).lower()
    complaint_id = row.get("complaint_id", "")
    
    # Determine Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            break
            
    # Determine Category
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "flooding", "water"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "trash", "garbage", "rubbish"],
        "Noise": ["noise", "loud", "music", "party"],
        "Road Damage": ["damage", "crack", "pavement"],
        "Heritage Damage": ["heritage", "monument", "statue", "historic"],
        "Heat Hazard": ["heat", "hot"],
        "Drain Blockage": ["drain", "blockage", "clog"]
    }
    
    category = "Other"
    flag = "NEEDS_REVIEW"
    reason = "Category cannot be determined from description alone."
    
    for cat, kws in category_map.items():
        found_kw = next((kw for kw in kws if kw in description), None)
        if found_kw:
            category = cat
            flag = ""
            reason = f"Classified as {cat} because the description contains '{found_kw}'."
            break
            
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
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile, \
             open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
             
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception as e:
                    writer.writerow({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Failed to process row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error processing files: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
