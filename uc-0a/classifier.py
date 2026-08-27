import argparse
import csv

ALLOWED_CATEGORIES = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "streetlight": "Streetlight",
    "light": "Streetlight",
    "waste": "Waste",
    "garbage": "Waste",
    "noise": "Noise",
    "road": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage"
}

URGENT_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse"
]


def classify_complaint(row: dict) -> dict:

    complaint_text = row.get("description", "").lower()

    category = "Other"
    flag = ""

    for keyword, value in ALLOWED_CATEGORIES.items():
        if keyword in complaint_text:
            category = value
            break

    priority = "Standard"

    for word in URGENT_KEYWORDS:
        if word in complaint_text:
            priority = "Urgent"
            break

    reason = f"Detected from complaint text: {complaint_text}"

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

    with open(input_path, newline='', encoding='utf-8') as csvfile:

        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)

            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Failed to process complaint",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline='', encoding='utf-8') as outfile:

        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag"
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for item in results:
            writer.writerow(item)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")