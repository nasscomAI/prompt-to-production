import csv

input_file = "../data/budget/ward_budget.csv"
output_file = "growth_output.csv"

totals = {}

with open(input_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        ward = row[list(row.keys())[0]]
        value = row[list(row.keys())[-1]]

        try:
            amount = float(value)
        except:
            continue   # skip non-numeric values

        if ward not in totals:
            totals[ward] = 0

        totals[ward] += amount

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ward", "total_budget"])

    for ward, total in totals.items():
        writer.writerow([ward, total])

print("Budget totals saved to growth_output.csv")