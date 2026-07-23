import argparse
import csv

SEVERITY_WORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
}

CATEGORY_RULES = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogging", "water logged"],
    "Streetlight": ["streetlight", "street light", "light not working"],
    "Waste": ["garbage", "waste", "trash", "dump"],
    "Noise": ["noise", "loud", "sound"],
    "Road Damage": ["road damage", "crack", "broken road"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat", "hot pavement", "heatwave"],
    "Drain Blockage": ["drain", "sewer", "blockage", "clogged"]
}


def classify_complaint(row):
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    text = description.lower()

    category = None
    matches = []

    for cat, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            matches.append(cat)

    if len(matches) == 1:
        category = matches[0]
        flag = ""
    elif len(matches) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    priority = (
        "Urgent"
        if any(word in text for word in SEVERITY_WORDS)
        else "Standard"
    )

    reason = (
        f'Classified using description text: "{description[:80]}"'
        if description
        else "No description provided."
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path, output_path):
    fieldnames = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            try:
                writer.writerow(classify_complaint(row))
            except Exception as e:
                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Processing error: {e}",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()
    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")