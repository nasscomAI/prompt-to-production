import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

PRIORITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

# Category keyword mapping (NEW)
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pit", "road hole"],
    "Flooding": ["flood", "waterlogging", "water log"],
    "Streetlight": ["streetlight", "light not working", "dark"],
    "Waste": ["garbage", "waste", "trash", "dump"],
    "Noise": ["noise", "loud", "sound"],
    "Road Damage": ["road damage", "broken road", "cracked road"],
    "Heritage Damage": ["heritage", "monument", "temple damage"],
    "Heat Hazard": ["heat", "extreme sun", "no shade"],
    "Drain Blockage": ["drain", "sewer", "blocked drainage"]
}


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }

    desc = description.lower()
    category = "Other"
    flag = ""
    matched_word = None

    # ---------------- CATEGORY DETECTION ----------------
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for word in keywords:
            if word in desc:
                category = cat
                matched_word = word  # capture actual word
                break
        if category != "Other":
            break

    # Ambiguity check
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # ---------------- PRIORITY DETECTION ----------------
    priority = "Standard"
    severity_word = None

    for word in PRIORITY_KEYWORDS:
        if word in desc:
            priority = "Urgent"
            severity_word = word
            break

    if "minor" in desc or "not urgent" in desc:
        priority = "Low"

    # ---------------- REASON (FIXED) ----------------
    if severity_word:
        reason = f"Detected keyword '{severity_word}' in the complaint."
    elif matched_word:
        reason = f"Detected keyword '{matched_word}' in the complaint."
    else:
        reason = "Description unclear for classification."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline='', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Error processing row.",
                    "flag": "NEEDS_REVIEW"
                }

            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()
    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")