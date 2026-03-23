import argparse
import csv

# Allowed categories
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Keywords for Urgent priority
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", row.get("id", "UNKNOWN"))
    
    category = "Other"
    priority = "Standard"
    reason = "No specific details provided."
    flag = ""
    
    # Determine Priority based on Enforcement rules
    found_urgent_words = [word for word in URGENT_KEYWORDS if word in description]
    if found_urgent_words:
        priority = "Urgent"
        
    # Determine Category & Reason
    if any(w in description for w in ["pothole"]):
        category = "Pothole"
        reason = f"Mentioned '{[w for w in ['pothole'] if w in description][0]}'"
    elif any(w in description for w in ["flood", "water"]):
        category = "Flooding"
        reason = "Mentioned water or flooding issues."
    elif any(w in description for w in ["light", "dark", "bulb"]):
        category = "Streetlight"
        reason = "Mentioned lighting issues."
    elif any(w in description for w in ["garbage", "trash", "waste", "smell"]):
        category = "Waste"
        reason = "Mentioned garbage or waste."
    elif any(w in description for w in ["loud", "music", "noise"]):
        category = "Noise"
        reason = "Mentioned noise complaints."
    elif not description or len(description.strip()) < 5:
        flag = "NEEDS_REVIEW"
        reason = "Description too short or missing."
    else:
        flag = "NEEDS_REVIEW"
        reason = "Category ambiguous based on description."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    try:
                        result = classify_complaint(row)
                        writer.writerow(result)
                    except Exception as e:
                        print(f"Skipping bad row due to error: {e}")
                        
    except FileNotFoundError:
        print(f"Error: Could not find the input file at {input_path}")
    except Exception as e:
        print(f"Error processing files: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")