"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(text):

    severity_keywords = [
        "injury","child","school","hospital","ambulance",
        "fire","hazard","fell","collapse"
    ]

    categories = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "noise": "Noise",
        "road": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage"
    }

    text_lower = text.lower()

    category = "Other"
    for key in categories:
        if key in text_lower:
            category = categories[key]
            break

    priority = "Standard"
    for word in severity_keywords:
        if word in text_lower:
            priority = "Urgent"
            break

    reason = f"Complaint contains keywords related to {category}"
    flag = ""

    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):

    import csv

    with open(input_file, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        with open(output_file, "w", newline='', encoding="utf-8") as outfile:
            fieldnames = reader.fieldnames + ["category","priority","reason","flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()

            for row in reader:
                text = row["description"]

                category, priority, reason, flag = classify_complaint(text)

                row["category"] = category
                row["priority"] = priority
                row["reason"] = reason
                row["flag"] = flag

                writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
