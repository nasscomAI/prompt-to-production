import csv


def calculate_growth(input_file, output_file):

    results = []

    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                ward = row.get("ward", "")
                category = row.get("category", "")
                previous = float(row.get("previous_budget", 0))
                current = float(row.get("current_budget", 0))

                if previous == 0:
                    growth = 0
                else:
                    growth = ((current - previous) / previous) * 100

                results.append({
                    "ward": ward,
                    "category": category,
                    "growth_percent": round(growth, 2),
                    "flag": ""
                })

            except Exception as e:
                results.append({
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "growth_percent": "",
                    "flag": str(e)
                })

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["ward", "category", "growth_percent", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":

    input_file = "../data/budget/ward_budget.csv"
    output_file = "growth_output.csv"

    calculate_growth(input_file, output_file)
