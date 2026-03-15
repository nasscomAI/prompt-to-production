"""
UC-0C app.py — Budget Growth Analyzer
Reads ward_budget.csv and calculates growth per ward and category.
"""

import argparse
import csv
import os


def calculate_growth(old_value, new_value):
    try:
        old_value = float(old_value)
        new_value = float(new_value)

        if old_value == 0:
            return 0

        growth = ((new_value - old_value) / old_value) * 100
        return "{round(growth, 2)}"

    except (ValueError, TypeError):
        return "INVALID"


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyzer")

    parser.add_argument(
        "--input",
        default="../data/budget/ward_budget.csv",
        help="Path to ward budget dataset"
    )

    parser.add_argument(
        "--output",
        default="growth_output.csv",
        help="Output CSV file"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found -> {args.input}")
        return

    results = []

    with open(args.input, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            ward = row.get("ward", "")
            category = row.get("category", "")
            prev_budget = row.get("previous_budget", 0)
            curr_budget = row.get("current_budget", 0)

            growth = calculate_growth(prev_budget, curr_budget)

            results.append({
                "ward": ward,
                "category": category,
                "growth_percent": growth
            })

    with open(args.output, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["ward", "category", "growth_percent"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print(f"Growth report generated: {args.output}")


if __name__ == "__main__":
    main()