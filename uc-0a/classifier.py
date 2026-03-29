import argparse
import csv

def classify_complaint(row: dict) -> dict:
    complaint_text = row.get("complaint", "").lower()

    # Default values
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    # CATEGORY LOGIC
    if "pothole" in complaint_text or "hole" in complaint_text:
        category = "Pothole"
    elif "flood" in complaint_text or "water" in complaint_text:
        category = "Flooding"
    elif "light" in complaint_text:
        category = "Streetlight"
    elif "garbage" in complaint_text or "waste" in complaint_text:
        category = "Waste"
    elif "noise" in complaint_text or "loud" in complaint_text:
        category = "Noise"
    elif "road" in complaint_text and "damage" in complaint_text:
        category = "Road Damage"
    elif "heritage" in complaint_text or "monument" in complaint_text:
        category = "Heritage Damage"
    elif "heat" in complaint_text or "hot" in complaint_text:
        category = "Heat Hazard"
    elif "drain" in complaint_text:
        category = "Drain Blockage"

    # PRIORITY LOGIC
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    if any(word in complaint_text for word in urgent_keywords):
        priority = "Urgent"
    elif len(complaint_text) < 20:
        priority = "Low"

    # REASON
    reason = f"Classified as {category} based on keywords in complaint"

    # FLAG (if unclear)
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                # If error, still add row with flag
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Error processing row",
                    "flag": "NEEDS_REVIEW"
                })

    # Write output
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")