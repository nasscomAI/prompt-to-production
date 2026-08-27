import argparse
import csv

# Allowed categories (STRICT)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

# Urgent keywords
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    text = row.get("complaint", "").lower()

    # --- CATEGORY ---
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

    # Ensure strict category
    if category not in ALLOWED_CATEGORIES:
        category = "Other"

    # --- PRIORITY ---
    if any(word in text for word in URGENT_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # --- REASON ---
    reason = f"Detected keywords from complaint: {text[:60]}"

    # --- FLAG ---
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

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Handle bad row without crashing
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

    except Exception as e:
        print("Error reading input file:", e)
        return

    # Write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print("Error writing output file:", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")