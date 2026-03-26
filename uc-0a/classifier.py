import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogging", "overflow"],
    "Streetlight": ["streetlight", "light not working", "dark"],
    "Waste": ["garbage", "trash", "waste"],
    "Noise": ["noise", "loud", "sound"],
    "Road Damage": ["road broken", "damaged road"],
    "Drain Blockage": ["drain", "sewage", "blocked"],
    "Heat Hazard": ["heat", "no shade"],
    "Heritage Damage": ["heritage", "monument"]
}


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "")
    complaint_id = row.get("complaint_id", "")

    if not description or not isinstance(description, str):
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Invalid or missing description",
            "flag": "NEEDS_REVIEW"
        }

    text = description.lower()

    matched_categories = []
    matched_keyword = None

    # Category detection
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                matched_categories.append(category)
                matched_keyword = kw
                break

    # Handle category + ambiguity
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority detection
    priority = "Standard"
    severity_word = None

    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"
            severity_word = word
            break

    # Reason generation
    if matched_keyword:
        reason = f"Classified as {category} because '{matched_keyword}' found in description"
    else:
        reason = f"Classified as {category} due to lack of clear category keywords"

    if severity_word:
        reason += f"; marked Urgent due to '{severity_word}'"

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
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception:
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Error processing row",
                        "flag": "NEEDS_REVIEW"
                    })

    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
