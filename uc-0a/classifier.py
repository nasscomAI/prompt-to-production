"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

severity_keywords = [
    "injury","child","school","hospital",
    "ambulance","fire","hazard","fell","collapse"
]

allowed_categories = [
    "Pothole","Flooding","Streetlight","Waste","Noise",
    "Road Damage","Heritage Damage","Heat Hazard",
    "Drain Blockage","Other"
]

def classify_complaint(row: dict) -> dict:

    text = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")

    # Category detection
    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "water" in text:
        category = "Flooding"
    elif "streetlight" in text or "lamp" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text:
        category = "Waste"
    elif "noise" in text:
        category = "Noise"
    elif "road damage" in text:
        category = "Road Damage"
    elif "heritage" in text:
        category = "Heritage Damage"
    elif "heat" in text:
        category = "Heat Hazard"
    elif "drain" in text:
        category = "Drain Blockage"
    else:
        category = "Other"

    # Priority detection
    if any(word in text for word in severity_keywords):
        priority = "Urgent"
        reason = "Severity keywords were detected in the complaint description, requiring urgent attention."
    else:
        priority = "Standard"
        if category == "Other":
            reason = "The complaint could not be mapped to a predefined category."
        else:
            reason = f"The complaint was classified as {category} based on the description."

    # Flag ambiguity
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }



def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id",""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Error processing complaint",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline='', encoding='utf-8') as outfile:
        fieldnames = ["complaint_id","category","priority","reason","flag"]
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
