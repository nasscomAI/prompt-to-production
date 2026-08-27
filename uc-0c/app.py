"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
import csv


def load_dataset(path):
    rows = []
    null_rows = []

    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append(row)
            rows.append(row)

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_spend = None

    for row in filtered:
        period = row["period"]
        actual = row["actual_spend"]

        if actual == "" or actual is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "FLAGGED",
                "formula": "NULL actual_spend — growth not computed"
            })
            prev_spend = None
            continue

        actual = float(actual)

        if prev_spend is None:
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth": "N/A",
                "formula": "First data point — no previous value"
            })
        else:
            growth = ((actual - prev_spend) / prev_spend) * 100
            formula = f"(({actual}-{prev_spend})/{prev_spend})*100"
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth": f"{growth:.1f}%",
                "formula": formula
            })

        prev_spend = actual

    return results


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type != "MoM":
        raise ValueError("Only MoM growth supported")

    rows, null_rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    with open(args.output, "w", newline='', encoding="utf-8") as f:
        fieldnames = ["period", "actual_spend", "growth", "formula"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print("Growth output written to", args.output)


if __name__ == "__main__":
    main()