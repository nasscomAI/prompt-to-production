import csv
import argparse


def load_dataset(input_path):
    data = []
    null_rows = []

    with open(input_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append(row)
            data.append(row)

    print("Total rows loaded:", len(data))
    print("Null rows found:", len(null_rows))

    return data, null_rows


def compute_growth(data, ward, category):
    results = []

    # Filter data
    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    prev_value = None

    for row in filtered:
        period = row["period"]
        actual = row["actual_spend"]

        if actual == "" or actual is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "growth": "NULL",
                "formula": "Skipped due to NULL actual_spend"
            })
            prev_value = None
            continue

        actual = float(actual)

        if prev_value is None:
            growth = 0
            formula = "No previous value"
        else:
            growth = ((actual - prev_value) / prev_value) * 100
            formula = f"(({actual} - {prev_value}) / {prev_value}) * 100"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "growth": round(growth, 2),
            "formula": formula
        })

        prev_value = actual

    return results


def save_output(output_path, results):
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["period", "ward", "category", "growth", "formula"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for row in results:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type not in ["MoM", "YoY"]:
        print("Invalid growth type. Use MoM or YoY")
        return

    print("Loading dataset...")

    data, null_rows = load_dataset(args.input)

    print("Computing growth...")

    results = compute_growth(data, args.ward, args.category)

    save_output(args.output, results)

    print("Output written to:", args.output)


if __name__ == "__main__":
    main()