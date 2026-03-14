import argparse
import csv

CATEGORY_KEYWORDS = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "streetlight": "Streetlight",
    "light": "Streetlight",
    "waste": "Waste",
    "garbage": "Waste",
    "noise": "Noise",
    "road damage": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage"
}

SEVERITY_KEYWORDS = [
    "injury","child","school","hospital",
    "ambulance","fire","hazard","fell","collapse"
]


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    text = description.lower()

    category = "Other"
    reason = "No clear category keyword detected."
    flag = ""

    # Category detection
    for keyword, cat in CATEGORY_KEYWORDS.items():
        if keyword in text:
            category = cat
            reason = f'Detected keyword "{keyword}" in complaint.'
            break

    # Priority detection
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"
            reason += f' Severity keyword "{word}" present.'
            break

    # Ambiguity flag
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

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag"
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception as e:
                    writer.writerow({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")

