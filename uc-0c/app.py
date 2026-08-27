"""
UC-0C Budget Growth Calculator
Computes per-period growth for a specific ward and category.
"""

import argparse
import csv


def load_dataset(file_path):
    required_cols = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    ]

    rows = []

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column: {col}")

        for row in reader:
            rows.append(row)

    return rows


def compute_growth(data, ward, category, growth_type):

    if growth_type != "MoM":
        raise ValueError("Only MoM growth is supported for this task.")

    filtered = [
        r for r in data if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_value = None

    for row in filtered:
        period = row["period"]
        spend = row["actual_spend"]
        notes = row["notes"]

        if spend == "" or spend is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "NULL VALUE – growth not computed",
                "flag": f"NULL VALUE ({notes})"
            })
            prev_value = None
            continue

        spend = float(spend)

        if prev_value is None:
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth": "N/A",
                "formula": "First period – no previous value",
                "flag": ""
            })
        else:
            growth = ((spend - prev_value) / prev_value) * 100
            formula = f"(({spend} - {prev_value}) / {prev_value}) * 100"

            results.append({
                "period": period,
                "actual_spend": spend,
                "growth": f"{growth:.2f}%",
                "formula": formula,
                "flag": ""
            })

        prev_value = spend

    return results


def write_output(results, output_path):

    fieldnames = ["period", "actual_spend", "growth", "formula", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in results:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    dataset = load_dataset(args.input)

    results = compute_growth(
        dataset,
        args.ward,
        args.category,
        args.growth_type
    )

    write_output(results, args.output)

    print(f"Growth results written to {args.output}")


if __name__ == "__main__":
    main()