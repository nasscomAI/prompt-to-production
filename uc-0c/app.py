import csv

input_file = "../data/budget/ward_budget.csv"
output_file = "growth_output.csv"

with open(input_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    data = list(reader)

# Simple processing (copy data)
processed_data = []

for row in data:
    processed_data.append(row)

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(processed_data)

print("Growth output created ✅")