import csv

input_file = "../data/budget/ward_budget.csv"
output_file = "growth_output.csv"

def calculate_growth():
    output_rows = []

    with open(input_file, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                budgeted = row["budgeted_amount"]
                actual = row["actual_spend"]

                # skip rows with empty values
                if budgeted == "" or actual == "":
                    continue

                budgeted = float(budgeted)
                actual = float(actual)

                growth = actual - budgeted

                output_rows.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "budgeted_amount": budgeted,
                    "actual_spend": actual,
                    "growth": growth
                })

            except:
                continue

    with open(output_file, "w", newline="") as file:
        fieldnames = ["period","ward","category","budgeted_amount","actual_spend","growth"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(output_rows)

    print("Growth file generated:", output_file)

if __name__ == "__main__":
    calculate_growth()
