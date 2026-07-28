import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]


def classify_complaint(row):
    text = row.get("description", "").lower()

    category = "Other"

    if any(word in text for word in ["pothole", "crater"]):
        category = "Pothole"
    elif any(word in text for word in ["flood", "waterlogging", "water logged"]):
        category = "Flooding"
    elif any(word in text for word in ["streetlight", "street light", "lamp"]):
        category = "Streetlight"
    elif any(word in text for word in ["garbage", "waste", "trash"]):
        category = "Waste"
    elif any(word in text for word in ["noise", "loud", "speaker"]):
        category = "Noise"
    elif any(word in text for word in ["road", "crack", "damaged road"]):
        category = "Road Damage"
    elif any(word in text for word in ["heritage", "monument"]):
        category = "Heritage Damage"
    elif any(word in text for word in ["heat", "hot"]):
        category = "Heat Hazard"
    elif any(word in text for word in ["drain", "sewer"]):
        category = "Drain Blockage"

    priority = "Standard"
    if any(word in text for word in SEVERITY_KEYWORDS):
        priority = "Urgent"

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    reason = f"Detected keywords from complaint: {text[:60]}"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path, output_path):
    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag",
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                writer.writerow(classify_complaint(row))
            except Exception:
                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classification failed",
                    "flag": "NEEDS_REVIEW",
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")