"""
UC-0C app.py — Infrastructure Spend Growth Calculator
"""
import argparse
import csv


def load_dataset(path):
    data = []
    null_rows = []

    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required.issubset(reader.fieldnames):
            raise ValueError("Dataset missing required columns")

        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append(row)
            data.append(row)

    if null_rows:
        print(f"Found {len(null_rows)} rows with null actual_spend values:")
        for r in null_rows:
            print(f'{r["period"]} | {r["ward"]} | {r["category"]} | reason: {r["notes"]}')

    return data


def compute_growth(data, ward, category, growth_type):
    if growth_type != "MoM":
        raise ValueError("Only MoM growth supported. Refusing to guess formula.")

    filtered = [
        r for r in data
        if r["ward"] == ward and r["category"] == category
    ]

    if not filtered:
        raise ValueError("No matching rows found for ward/category")

    filtered.sort(key=lambda x: x["period"])

    results = []

    prev_spend = None

    for row in filtered:
        spend = row["actual_spend"]

        if spend == "" or spend is None:
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "FLAGGED_NULL",
                "formula": "N/A",
                "notes": row["notes"]
            })
            prev_spend = None
            continue

        spend = float(spend)

        if prev_spend is None:
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": spend,
                "growth": "N/A",
                "formula": "N/A",
                "notes": ""
            })
        else:
            growth = ((spend - prev_spend) / prev_spend) * 100
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": spend,
                "growth": round(growth, 2),
                "formula": "(current - previous) / previous * 100",
                "notes": ""
            })

        prev_spend = spend

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data = load_dataset(args.input)

    results = compute_growth(data, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()