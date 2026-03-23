import argparse
import csv

def classify_complaint(row: dict) -> dict:
    text = row.get("description", "").lower()

    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "water" in text:
        category = "Flooding"
    elif "light" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text:
        category = "Waste"
    elif "noise" in text:
        category = "Noise"
    elif "road" in text:
        category = "Road Damage"
    elif "drain" in text:
        category = "Drain Blockage"
    else:
        category = "Other"

    urgent_keywords = [
        "injury", "child", "school", "hospital",
        "ambulance", "fire", "hazard", "fell", "collapse"
    ]

    if any(word in text for word in urgent_keywords):
        priority = "Urgent"
    else:
        priority = "Standard"

    reason = f"Detected keywords in complaint: {text}"
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r') as infile, open(output_path, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                row.update(result)
            except Exception:
                row.update({
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Error processing row",
                    "flag": "NEEDS_REVIEW"
                })
            writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
