"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "")

    if not description or len(description.split()) < 5:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or too short",
            "flag": "NEEDS_REVIEW"
        }

    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    categories = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "waste": "Waste",
        "noise": "Noise",
        "road damage": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage"
    }

    category_keyword = None
    category = "Other"
    for keyword, cat in categories.items():
        if keyword in description.lower():
            category = cat
            category_keyword = keyword
            break

    severity_keyword = None
    priority = "Standard"
    for keyword in severity_keywords:
        if keyword in description.lower():
            priority = "Urgent"
            severity_keyword = keyword
            break

    if priority == "Urgent":
        reason = f"Contains '{severity_keyword}' indicating urgency"
    elif category_keyword:
        reason = f"Contains '{category_keyword}' identifying the issue"
    else:
        reason = "No specific keywords found in description"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "STABLE" if category != "Other" else "NEEDS_REVIEW"
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, mode="r", newline="", encoding="utf-8") as infile, \
         open(output_path, mode="w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input file or directory")
    parser.add_argument("--output", required=True, help="Path to output file or directory")
    args = parser.parse_args()

    if os.path.isdir(args.input):
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        
        for filename in os.listdir(args.input):
            if filename.endswith(".csv"):
                input_file = os.path.join(args.input, filename)
                
                # Map test_[city].csv to results.[city].csv
                if filename.startswith("test_"):
                    city = filename[5:-4] # Extract [city]
                    output_filename = f"results.{city}.csv"
                else:
                    output_filename = "results." + filename
                
                output_file = os.path.join(args.output, output_filename)
                
                # Cleanup: Delete existing output file
                if os.path.exists(output_file):
                    print(f"Deleting existing file: {output_file}")
                    os.remove(output_file)
                
                print(f"Processing {input_file} -> {output_file}")
                batch_classify(input_file, output_file)
        print(f"Done. Batch results written to {args.output}")
    else:
        # Cleanup for single file mode too
        if os.path.exists(args.output):
            print(f"Deleting existing file: {args.output}")
            os.remove(args.output)
        batch_classify(args.input, args.output)
        print(f"Done. Results written to {args.output}")
