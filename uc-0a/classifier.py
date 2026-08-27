"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on agent rules.
    """
    complaint_id = row.get("complaint_id", "unknown")
    description = row.get("description", "")
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Normal",
            "reason": "Missing description",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Priority enforcement rule
    urgent_triggers = ["injury", "child", "school", "hospital"]
    priority = "Normal"
    reason_words = []
    
    for trigger in urgent_triggers:
        if trigger in desc_lower:
            priority = "Urgent"
            reason_words.append(trigger)
            
    # Category enforcement rule
    category = "Other"
    flag = "OK"
    
    if "pothole" in desc_lower or "road" in desc_lower:
        category = "Pothole"
        reason_words.append("pothole/road text found")
    elif "flood" in desc_lower or "rain" in desc_lower or "water" in desc_lower:
        category = "Flooding"
        reason_words.append("flood/rain text found")
    elif "light" in desc_lower or "dark" in desc_lower:
        category = "Streetlight"
        reason_words.append("light/dark text found")
    elif "garbage" in desc_lower or "waste" in desc_lower or "sanitation" in desc_lower:
        category = "Sanitation"
        reason_words.append("garbage/waste text found")
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_words.append("unclear description")
        
    reason = "Found words: " + ", ".join(reason_words) if reason_words else "Unclear description."
    
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
    Flags nulls, doesn't crash on bad rows, and produces output securely.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "error"),
                        "category": "Other",
                        "priority": "Normal",
                        "reason": f"Error parsing: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error processing batch: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
