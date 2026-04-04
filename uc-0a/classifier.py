"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using RICE enforcement rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Enforcement: Allowed Categories (Exact strings)
    # Keyword mapping for classification
    category_map = {
        "Pothole": ["pothole", "hole in road", "pitt"],
        "Flooding": ["flood", "waterlog", "overflow", "stagnant water"],
        "Streetlight": ["streetlight", "lamp", "dark", "street light"],
        "Waste": ["garbage", "trash", "waste", "rubbish", "dump"],
        "Noise": ["noise", "loud", "music", "sound", "shouting"],
        "Road Damage": ["crack", "broken road", "uneven", "manhole"],
        "Heritage Damage": ["monument", "heritage", "statue", "historical"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "burning", "fire hazard"],
        "Drain Blockage": ["drain", "sewer", "clog", "choke"],
    }
    
    category = "Other"
    for cat, keywords in category_map.items():
        if any(kw in description for kw in keywords):
            category = cat
            break
            
    # 2. Enforcement: Priority (Urgent keywords)
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    triggered_keyword = None
    
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            triggered_keyword = kw
            break
            
    if priority != "Urgent" and ("soon" in description or "fast" in description):
        priority = "Standard" # Simple heuristic
    
    # 3. Enforcement: Reason (One sentence citing words)
    if triggered_keyword:
        reason = f"Classified as {priority} because description mentions '{triggered_keyword}'."
    else:
        reason = f"Classified as {category} based on the mention of related infrastructure in the description."

    # 4. Enforcement: Flag (Ambiguity)
    flag = ""
    if category == "Other" or len(description.split()) < 3:
        flag = "NEEDS_REVIEW"
        
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
    Handles nulls and missing files.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            results = []
            
            for row in reader:
                if not row.get("description"):
                    # Handle nulls/empty rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "N/A"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description field.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Don't crash on bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "N/A"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

        if results:
            keys = results[0].keys()
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Error during batch processing: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
