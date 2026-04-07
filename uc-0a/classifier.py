import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury","child","school","hospital",
    "ambulance","fire","hazard","fell","collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood"],
    "Streetlight": ["streetlight","light not working"],
    "Waste": ["garbage","waste","trash"],
    "Noise": ["noise","loud"],
    "Road Damage": ["road damage","crack"],
    "Heritage Damage": ["heritage","monument"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain","blocked drain"]
}

def classify_complaint(row):
    text = row["description"].lower()

    category = "Other"

    for cat, words in CATEGORY_KEYWORDS.items():
        if any(word in text for word in words):
            category = cat
            break

    priority = "Standard"

    if any(word in text for word in SEVERITY_KEYWORDS):
        priority = "Urgent"

    reason = f"Detected keywords in complaint: {category}"

    flag = ""

    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row["complaint_id"],
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path, output_path):

    results = []

    with open(input_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id","unknown"),
                    "category": "",
                    "priority": "",
                    "reason": "processing error",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["complaint_id","category","priority","reason","flag"]
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print("Classification complete")