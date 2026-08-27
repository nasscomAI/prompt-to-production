"""
UC-0C app.py — Budget growth calculator
"""

import csv
import argparse


def calculate_growth(input_file, output_file):

    rows = []

    with open(input_file, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            prev = float(row.get("previous_budget", 0))
            curr = float(row.get("current_budget", 0))

            if prev == 0:
                growth = 0
            else:
                growth = ((curr - prev) / prev) * 100

            row["growth_percent"] = round(growth, 2)

            rows.append(row)

    with open(output_file, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(f, fieldnames=rows[0].keys())

        writer.writeheader()
        writer.writerows(rows)

    print("Budget growth calculated")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    calculate_growth(args.input, args.output)


if __name__ == "__main__":
    main()