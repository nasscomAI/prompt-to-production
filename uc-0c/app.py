"""
UC-0C app.py — Complaint Statistics Application
Reads a complaint CSV file and shows summary statistics by category.
"""

import argparse
import csv


def generate_summary(input_file):
    """
    Read the complaint results CSV and count complaints by category and priority.
    """
    category_count = {}
    priority_count = {}

    try:
        with open(input_file, newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                category = row.get("category", "Unknown")
                priority = row.get("priority", "Unknown")

                # Count categories
                if category not in category_count:
                    category_count[category] = 0
                category_count[category] += 1

                # Count priorities
                if priority not in priority_count:
                    priority_count[priority] = 0
                priority_count[priority] += 1

    except FileNotFoundError:
        print("Error: Input file not found.")
        return None, None

    return category_count, priority_count


def main():
    parser = argparse.ArgumentParser(description="UC-0C Complaint Statistics")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to classified complaints CSV file"
    )

    args = parser.parse_args()

    category_count, priority_count = generate_summary(args.input)

    if category_count is None:
        return

    print("\nComplaint Summary by Category:")
    for category, count in category_count.items():
        print(f"{category}: {count}")

    print("\nComplaint Summary by Priority:")
    for priority, count in priority_count.items():
        print(f"{priority}: {count}")


if __name__ == "__main__":
    main()