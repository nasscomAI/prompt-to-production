"""
UC-0C — Number That Looks Right
Build using RICE + agents.md + skills.md + CRAFT workflow
"""

import argparse
import csv


def calculate_growth(input_path, output_path):
    """
    Read budget CSV and calculate growth between rows.
    Writes growth_output.csv
    """

    rows = []

    try:
        with open(input_path, newline='', encoding="utf-8") as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                rows.append(row)

        results = []
        prev_value = None

        for row in rows:

            year = row.get("year")
            revenue = float(row.get("revenue", 0))

            growth = ""

            if prev_value is not None and prev_value != 0:
                growth = round((revenue - prev_value) / prev_value, 2)

            results.append({
                "year": year,
                "revenue": revenue,
                "growth": growth
            })

            prev_value = revenue

        with open(output_path, "w", newline='', encoding="utf-8") as outfile:
            fieldnames = ["year", "revenue", "growth"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(results)

        print(f"Growth analysis written to {output_path}")

    except Exception as e:
        print("Error processing data:", str(e))


def main():

    parser = argparse.ArgumentParser(description="UC-0C Numeric Growth Analyzer")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to budget CSV file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write growth_output.csv"
    )

    args = parser.parse_args()

    calculate_growth(args.input, args.output)


if __name__ == "__main__":
    main()
