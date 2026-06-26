import argparse
import csv

# Allowed categories
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlogging", "water logged"],
    "Streetlight": ["streetlight", "street light", "lamp", "light not working"],
    "Waste": ["garbage", "waste", "trash", "dump"],
    "Noise": ["noise", "loud", "speaker", "construction"],
    "Road Damage": ["road damage", "damaged road", "crack", "broken road"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    "Heat Hazard": ["heat", "heatwave", "extreme heat"],
    "Drain Blockage": ["drain", "blocked drain", "clogged drain", "sewer"]
}

SEVERITY_KEYWORDS = [
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
    text = row.get("description", "").lower()

    category = "Other"

    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(word in text for word in keywords):
            category = cat
            break

    priority = "Standard"

    if any(word in text for word in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif category == "Other":
        priority = "Low"

    matched = []

    for words in CATEGORY_KEYWORDS.values():
        for word in words:
            if word in text:
                matched.append(word)

    severity_found = [w for w in SEVERITY_KEYWORDS if w in text]

    keywords = matched + severity_found

    if keywords:
        reason = f"Detected keywords: {', '.join(keywords)}."
    else:
        reason = "No matching keywords found."

    flag = ""

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

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag"
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)

            except Exception:

                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Classification failed.",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")
