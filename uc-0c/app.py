import csv

data = {}

with open("../data/budget/ward_budget.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        ward = row.get("ward", "")
        category = row.get("category", "")
        budget = row.get("actual_spend", "0")

        try:
            amount = float(budget)
        except:
            continue

        key = (ward, category)

        if key not in data:
            data[key] = 0

        data[key] += amount


# write output
with open("growth_output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Ward", "Category", "Total"])

    for (ward, category), total in data.items():
        writer.writerow([ward, category, round(total, 2)])

print("Done!")