import argparse
import csv


def load_dataset(path):
    data = []
    null_rows = []

    with open(path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append(row)
            data.append(row)

    return data, null_rows


def compute_growth(data, ward, category, growth_type):
    if not growth_type:
        raise ValueError("Growth type must be specified")

    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]

    results = []
    prev_value = None

    for row in filtered:
        period = row["period"]
        actual = row["actual_spend"]
        notes = row["notes"]

        if actual == "" or actual is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NA",
                "formula": "NA",
                "flag": f"NEEDS_REVIEW ({notes})"
            })
            prev_value = None
            continue

        actual = float(actual)

        if prev_value is None:
            growth = "NA"
            formula = "NA"
        else:
            growth_val = ((actual - prev_value) / prev_value) * 100
            growth = f"{round(growth_val, 2)}%"
            formula = f"(({actual} - {prev_value}) / {prev_value}) * 100"

        results.append({
            "period": period,
            "actual_spend": actual,
            "growth": growth,
            "formula": formula,
            "flag": ""
        })

        prev_value = actual

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data, nulls = load_dataset(args.input)

    results = compute_growth(data, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline='', encoding='utf-8') as file:
        fieldnames = ["period", "actual_spend", "growth", "formula", "flag"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()