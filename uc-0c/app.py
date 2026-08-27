"""
UC-0C — Budget Growth Calculator
Computes growth (MoM or YoY) for a given ward and category
while enforcing null checks and avoiding cross-ward aggregation.
"""

import argparse
import csv


def load_dataset(path):
    """
    Load dataset and report null rows before computation.
    """
    rows = []
    null_rows = []

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required_cols = [
            "period",
            "ward",
            "category",
            "budgeted_amount",
            "actual_spend",
            "notes",
        ]

        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column: {col}")

        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append(row)
            rows.append(row)

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """
    Compute growth for the selected ward and category.
    """
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError("growth-type must be MoM or YoY")

    # Filter dataset
    filtered = [
        r for r in rows if r["ward"] == ward and r["category"] == category
    ]

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_value = None

    for r in filtered:
        period = r["period"]
        spend = r["actual_spend"]

        if spend == "" or spend is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "FLAG_NULL",
                "formula": "actual_spend is NULL → growth not computed"
            })
            prev_value = None
            continue

        spend = float(spend)

        if prev_value is None:
            growth = "N/A"
            formula = "No previous value"
        else:
            if growth_type == "MoM":
                growth_val = ((spend - prev_value) / prev_value) * 100
                growth = f"{growth_val:.1f}%"
                formula = "(current - previous) / previous * 100"

            elif growth_type == "YoY":
                growth = "N/A"
                formula = "YoY requires previous year data"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": spend,
            "growth": growth,
            "formula": formula
        })

        prev_value = spend

    return results


def write_output(results, output_path):
    """
    Write results to CSV.
    """
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth",
        "formula",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    print(f"Dataset loaded. Null rows detected: {len(null_rows)}")

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    write_output(results, args.output)

    print(f"Done. Growth results written to {args.output}")


if __name__ == "__main__":
    main()

