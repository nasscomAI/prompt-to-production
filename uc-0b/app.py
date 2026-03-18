"""
UC-0B app.py — Complaint Query Application
Simple application to search and display complaints from a CSV file.
"""

import argparse
import csv


def search_complaints(input_file, keyword):
    """
    Search complaints in the CSV file based on a keyword.
    """
    results = []

    try:
        with open(input_file, newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                description = row.get("description", "").lower()

                if keyword.lower() in description:
                    results.append(row)

    except FileNotFoundError:
        print("Error: Input file not found.")
        return []

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0B Complaint Search Application")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to complaint CSV file"
    )

    parser.add_argument(
        "--keyword",
        required=True,
        help="Keyword to search in complaint descriptions"
    )

    args = parser.parse_args()

    results = search_complaints(args.input, args.keyword)

    if not results:
        print("No matching complaints found.")
        return

    print(f"\nFound {len(results)} matching complaints:\n")

    for row in results:
        complaint_id = row.get("complaint_id", "N/A")
        description = row.get("description", "N/A")

        print(f"Complaint ID: {complaint_id}")
        print(f"Description : {description}")
        print("-" * 40)


if __name__ == "__main__":
    main()