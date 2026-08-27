import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row based on RICE enforcement rules."""
    desc = row.get("description", "").lower()
    
    # Priority keywords check
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in urgent_keywords:
        if kw in desc:
            priority = "Urgent"
            break
            
    # Default outputs
    first_sentence = desc.split('.')[0] + "."  
    reason = f'Contains specific phrase: "{first_sentence.capitalize()}"'
    flag = ""
    category = "Other"

    # Taxonomy enforcement logic
    if "pothole" in desc:
        category = "Pothole"
    elif " streetlight" in desc or "lights out" in desc or "dark" in desc:
        category = "Streetlight"
        if "heritage" in desc:
            flag = "NEEDS_REVIEW"
    elif "flood" in desc or "rain" in desc or "water" in desc:
        category = "Flooding"
        if "drain blocked" in desc:
             flag = "NEEDS_REVIEW"
    elif "garbage" in desc or "waste" in desc or "animal" in desc:
        category = "Waste"
    elif "music" in desc or "noise" in desc:
        category = "Noise"
    elif "manhole" in desc:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif "crack" in desc or "footpath" in desc:
        category = "Road Damage"
        
    row["category"] = category
    row["priority"] = priority
    row["reason"] = reason
    row["flag"] = flag
    return row


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    results = []
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        # We assume the input CSV has no category, priority, reason, flag columns.
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        for row in reader:
            if not row.get("description"):
                continue
            classified_row = classify_complaint(row)
            results.append(classified_row)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
