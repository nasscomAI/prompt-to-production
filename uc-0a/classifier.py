import csv

CATEGORY_MAP = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogging"],
    "Streetlight": ["streetlight", "light"],
    "Waste": ["garbage", "waste", "trash"],
    "Noise": ["noise", "loud"],
    "Road Damage": ["road damage", "broken road"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain", "sewage", "block"]
}

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row):
    text = row.get("complaint_text", "").lower()
    complaint_id = row.get("complaint_id", "")

    if not text:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    # Category detection
    category = "Other"
    for cat, keywords in CATEGORY_MAP.items():
        for word in keywords:
            if word in text:
                category = cat
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
    reason = f"Detected from text: {text[:50]}"

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


def batch_classify():
    input_path = "data/city-test-files/test_pune.csv"
    output_path = "uc-0a/results_pune.csv"

    print("Reading input file...")

    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    print("Total rows:", len(rows))

    with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in rows:
            result = classify_complaint(row)
            writer.writerow(result)

    print("File written to:", output_path)


if __name__ == "__main__":
    print("Starting classifier...")
    batch_classify()
    print("Done!")