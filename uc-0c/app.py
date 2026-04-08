import csv

INPUT_FILE = "../data/budget/ward_budget.csv"
OUTPUT_FILE = "growth_output.csv"


def read_budget(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def calculate_totals(rows):
    results = []

    for row in rows:
        ward = row["ward"]
        category = row["category"]

        budgeted = row["budgeted_amount"]
        actual = row["actual_spend"]

        # Skip rows where values are missing
        if budgeted == "" or actual == "":
            continue

        budgeted = float(budgeted)
        actual = float(actual)

        difference = actual - budgeted

        results.append({
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual,
            "difference": difference
        })

    return results


def save_results(results):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ward", "category", "budgeted_amount", "actual_spend", "difference"]
        )
        writer.writeheader()
        writer.writerows(results)


def main():
    rows = read_budget(INPUT_FILE)
    results = calculate_totals(rows)
    save_results(results)

    print("Growth analysis saved to", OUTPUT_FILE)


if __name__ == "__main__":
    main()