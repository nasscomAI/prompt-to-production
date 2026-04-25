"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based logic derived from agents.md.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Determine Category
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flooded", "flooding", "water", "drain blocked", "underpass"],
        "Streetlight": ["streetlight", "lights out", "flickering", "dark at night", "unlit"],
        "Waste": ["garbage", "bins", "waste", "dumped", "smell", "cleared"],
        "Noise": ["music", "noise", "drilling", "engines"],
        "Road Damage": ["cracked", "sinking", "road surface", "footpath", "tiles", "paving", "broken bench", "bubbling", "subsidence", "broken", "split branches", "collapsed", "crater"],
        "Heritage Damage": ["heritage", "ancient"],
        "Drain Blockage": ["drain", "blocked", "manhole"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "melting", "44°c", "45°c", "52°c", "temperature", "heatwave", "full sun", "burns"]
    }
    
    category = "Other"
    found_words = []
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in description:
                category = cat
                found_words.append(kw)
                break
        if category != "Other":
            break
            
    # 2. Determine Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    priority_evidence = []
    
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            priority_evidence.append(kw)
    
    if priority != "Urgent":
        # Low priority if it's noise or smell without urgent hazards
        if "noise" in description or "smell" in description:
            priority = "Low"
            
    # 3. Generate Reason
    if priority == "Urgent":
        reason = f"Classified as Urgent because description contains safety-critical words: {', '.join(priority_evidence)}."
    elif category != "Other":
        reason = f"Classified as {category} due to mentions of {', '.join(found_words)}."
    else:
        reason = "Classified as Other because description did not match specific category keywords."
        
    # 4. Set Flag
    flag = "NEEDS_REVIEW" if category == "Other" or not description else ""
    
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
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    
        if not results:
            print("No results to write.")
            return

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Fatal error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
