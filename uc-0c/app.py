"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

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
    prev = None

    for row in filtered:
        period = row["period"]
        actual = row["actual_spend"]

        # Handle NULL
        if actual == "" or actual is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NA",
                "formula": "NA",
                "flag": f"NULL value — {row.get('notes','')}"
            })
            prev = None
            continue

        actual = float(actual)

        if prev is None:
            growth = "NA"
            formula = "NA"
        else:
            if growth_type == "MoM":
                growth_val = ((actual - prev) / prev) * 100
                growth = f"{growth_val:.1f}%"
                formula = f"(({actual} - {prev}) / {prev}) * 100"
            else:
                raise ValueError("Unsupported growth type")

        results.append({
            "period": period,
            "actual_spend": actual,
            "growth": growth,
            "formula": formula,
            "flag": ""
        })

        prev = actual

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if not args.growth_type:
        raise ValueError("growth-type must be specified")

    rows, null_rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    with open(args.output, "w", newline='', encoding="utf-8") as f:
        fieldnames = ["period", "actual_spend", "growth", "formula", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()