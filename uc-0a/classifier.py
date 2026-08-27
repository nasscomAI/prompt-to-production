import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood"],
    "Streetlight": ["streetlight"],
    "Waste": ["waste", "garbage"],
    "Noise": ["noise", "drilling", "sound", "loud"],
    "Road Damage": ["crater", "crack", "road damage"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain"],
}

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()

    # Determine priority
    priority = "Standard"
    matched_severity_kw = None
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            matched_severity_kw = kw
            break

    # Determine category
    category = "Other"
    matched_category_kw = None
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in description:
                category = cat
                matched_category_kw = kw
                break
        if category != "Other":
            break

    # Determine flag
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    # Construct one-sentence reason citing specific words
    if category != "Other" and matched_severity_kw:
        reason = f"Classified as {category} and marked Urgent due to '{matched_category_kw}' and '{matched_severity_kw}' in description."
    elif category != "Other":
        reason = f"Classified as {category} because the description contains the word '{matched_category_kw}'."
    elif matched_severity_kw:
        reason = f"Marked Urgent because of '{matched_severity_kw}', but category is Other as no category keyword was found."
    else:
        reason = "Classified as Other because no known category or severity keywords were found in the description."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, mode="r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception:
                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Failed classification due to an unexpected processing error.",
                    "flag": "NEEDS_REVIEW"
                })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")