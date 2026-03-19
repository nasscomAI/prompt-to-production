import argparse
import csv

# Severity keywords trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Allowed categories
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Keyword mapping for categories
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole in road", "road pit"],
    "Flooding": ["flood", "waterlogged", "water accumulation", "overflow"],
    "Streetlight": ["streetlight", "lamp not working", "broken light"],
    "Waste": ["garbage", "waste", "dumping", "trash", "refuse"],
    "Noise": ["noise", "loud", "honking", "disturbance"],
    "Road Damage": ["crack", "road damage", "road broken", "uneven road"],
    "Heritage Damage": ["heritage", "monument", "historic building", "damage heritage"],
    "Heat Hazard": ["heat", "sun exposure", "burn", "hot surface"],
    "Drain Blockage": ["drain blocked", "sewage", "clogged drain", "drainage problem"]
}

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    result = {
        "complaint_id": row.get("complaint_id", ""),
        "category": "Other",
        "priority": "Standard",
        "reason": "",
        "flag": ""
    }

    # Category mapping
    matched = False
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc:
                result["category"] = category
                result["reason"] = f"Found keyword '{kw}' in description"
                matched = True
                break
        if matched:
            break

    # Priority
    urgent_triggered = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    if urgent_triggered:
        result["priority"] = "Urgent"
        if result["reason"]:
            result["reason"] += f"; urgency triggered by: {', '.join(urgent_triggered)}"
        else:
            result["reason"] = f"Urgency triggered by: {', '.join(urgent_triggered)}"

    # Flag ambiguous complaints
    if result["category"] == "Other":
        result["flag"] = "NEEDS_REVIEW"

    return result

def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                classified = classify_complaint(row)
                writer.writerow(classified)
            except Exception as e:
                print(f"Warning: Failed to process row {row.get('complaint_id')}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")