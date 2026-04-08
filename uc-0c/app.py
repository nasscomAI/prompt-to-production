"""
UC-0C — Budget Growth Analyzer
Reads ward_budget.csv and calculates budget growth.
"""

import csv

INPUT_FILE = "../data/budget/ward_budget.csv"
OUTPUT_FILE = "growth_output.csv"


def calculate_growth(previous, current):
    try:
        previous = float(previous)
        current = float(current)

        if previous == 0:
            return 0

        growth = ((current - previous) / previous) * 100
        return round(growth, 2)

    except:
        return 0


def main():

    with open(INPUT_FILE, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        rows = list(reader)

    results = []

    for row in rows:
        ward = row.get("ward")
        category = row.get("category")

        prev_budget = row.get("previous_year")
        curr_budget = row.get("current_year")

        growth = calculate_growth(prev_budget, curr_budget)

        results.append({
            "ward": ward,
            "category": category,
            "growth_percent": growth
        })

    with open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["ward", "category", "growth_percent"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print("Growth report created:", OUTPUT_FILE)


if __name__ == "__main__":
    main()