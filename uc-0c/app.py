import csv

def calculate_growth(input_file, output_file):
    rows = []

    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                prev = float(row["previous"])
                curr = float(row["current"])
                growth = curr - prev
                row["growth"] = growth
            except:
                row["growth"] = 0
            rows.append(row)

    fieldnames = list(rows[0].keys())

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("Growth calculation complete.")

if __name__ == "__main__":
    input_file = "../data/budget/ward_budget.csv"
    output_file = "growth_output.csv"
    calculate_growth(input_file, output_file)
