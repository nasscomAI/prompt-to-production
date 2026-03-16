"""
UC-X app.py — Integrated Complaint Processing Application
This program reads complaint data, classifies complaints,
and generates a simple summary report.
"""

import argparse
import csv


def classify(description):
    description = description.lower()

    if "pothole" in description:
        return "Pothole"
    elif "flood" in description or "waterlogging" in description:
        return "Flooding"
    elif "garbage" in description or "waste" in description:
        return "Garbage"
    elif "streetlight" in description or "light not working" in description:
        return "Streetlight"
    elif "water supply" in description or "no water" in description:
        return "Water Supply"
    else:
        return "Other"


def detect_priority(description):
    urgent_words = ["injury", "accident", "danger", "school", "hospital"]

    for word in urgent_words:
        if word in description.lower():
            return "Urgent"

    return "Normal"


def process_complaints(input_file, output_file):

    results = []
    category_count = {}
    priority_count = {}

    with open(input_file, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            complaint_id = row.get("complaint_id", "")
            description = row.get("description", "")

            category = classify(description)
            priority = detect_priority(description)

            results.append({
                "complaint_id": complaint_id,
                "category": category,
                "priority": priority
            })

            category_count[category] = category_count.get(category, 0) + 1
            priority_count[priority] = priority_count.get(priority, 0) + 1

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        fieldnames = ["complaint_id", "category", "priority"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print("\nComplaint Summary by Category")
    for k, v in category_count.items():
        print(f"{k}: {v}")

    print("\nComplaint Summary by Priority")
    for k, v in priority_count.items():
        print(f"{k}: {v}")


def main():

    parser = argparse.ArgumentParser(description="UC-X Integrated Complaint System")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to complaint CSV file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV file"
    )

    args = parser.parse_args()

    process_complaints(args.input, args.output)

    print(f"\nResults written to {args.output}")


if __name__ == "__main__":
    main()