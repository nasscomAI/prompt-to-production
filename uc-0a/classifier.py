import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "road hole"],
    "Flooding": ["flood", "waterlogging"],
    "Streetlight": ["streetlight", "light not working"],
    "Waste": ["garbage", "waste", "trash", "dump"],
    "Noise": ["noise", "loud"],
    "Road Damage": ["road damage", "broken road", "crack"],
    "Drain Blockage": ["drain", "blocked", "sewage"],
    "Heat Hazard": ["heat", "hot", "temperature"],
    "Heritage Damage": ["heritage", "monument", "historic"]
}

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    text = (
        row.get("description") or
        row.get("complaint") or
        row.get("text") or
        ""
    ).lower()
    if not text.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty complaint text",
            "flag": "NEEDS_REVIEW"
        }

    # Category detection
    category = "Other"
    matched_word = None

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for word in keywords:
            if word in text:
                category = cat
                matched_word = word
                break
        if category != "Other":
            break

    # Priority detection
    priority = "Standard"
    for word in URGENT_KEYWORDS:
        if word in text:
            priority = "Urgent"
            break

    # Reason
    if matched_word:
        reason = f"Keyword '{matched_word}' found in description indicating {category}"
    elif priority == "Urgent":
        reason = "Urgency keyword found but no matching category keyword"
    else:
        reason = "No clear category keyword found in description"

    # Flag
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
    with open(input_path, mode="r", encoding="utf-8") as infile, \
         open(output_path, mode="w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)

                combined_row = row.copy()
                combined_row.update(result)

                writer.writerow(combined_row)

            except Exception as e:
                row.update({
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test CSV")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
