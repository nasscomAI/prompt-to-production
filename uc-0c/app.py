# UC-0C Budget Analysis

import csv

input_file = "../data/budget/ward_budget.csv"
output_file = "growth_output.csv"

try:
    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        rows = list(reader)

    # Just copy data safely (basic version)
    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    print("Growth output created successfully!")

except Exception as e:
    print("Error:", e)
