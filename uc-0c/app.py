
"""
UC-0C app.py

Implements guarded growth computation for ward-level budget data.
Strictly enforces:
- No cross-ward or cross-category aggregation
- Explicit growth type
- Explicit null handling with reasons
- Formula disclosure per row

See README.md for expected behaviour and reference checks.
"""

import argparse
import csv
import sys
from datetime import datetime


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(path):
    """Load CSV, validate structure, and report null actual_spend rows."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])

        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        rows = list(reader)

    null_rows = [
        {
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "notes": r["notes"],
        }
        for r in rows
        if r["actual_spend"] is None or r["actual_spend"].strip() == ""
    ]

    return rows, null_rows


def parse_period(p):
    return datetime.strptime(p, "%Y-%m")


def compute_growth(rows, ward, category, growth_type):
    """Compute growth safely for a single ward and category."""
    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]

    if not filtered:
        raise ValueError("No data found for given ward and category")

    filtered.sort(key=lambda r: parse_period(r["period"]))

    results = []

    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]

        if actual is None or actual.strip() == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "FLAGGED",
                "formula_or_reason": row["notes"] or "Null actual_spend"
            })
            continue

        actual = float(actual)

        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual,
                    "growth": "N/A",
                    "formula_or_reason": "No previous month"
                })
                continue

            prev = filtered[i - 1]["actual_spend"]
            if prev is None or prev.strip() == "":
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual,
                    "growth": "FLAGGED",
                    "formula_or_reason": "Previous period actual_spend is NULL"
                })
                continue

            prev = float(prev)
            growth = (actual - prev) / prev
            formula = f"({actual:.2f} - {prev:.2f}) / {prev:.2f}"

        elif growth_type == "YoY":
            if i < 12:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual,
                    "growth": "N/A",
                    "formula_or_reason": "No prior year period"
                })
                continue

            prev = filtered[i - 12]["actual_spend"]
            if prev is None or prev.strip() == "":
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual,
                    "growth": "FLAGGED",
                    "formula_or_reason": "Prior year actual_spend is NULL"
                })
                continue

            prev = float(prev)
            growth = (actual - prev) / prev
            formula = f"({actual:.2f} - {prev:.2f}) / {prev:.2f}"

        else:
            raise ValueError("Unsupported growth type")

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual,
            "growth": round(growth * 100, 2),
            "formula_or_reason": formula
        })

    return results


def write_output(path, rows):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth",
        "formula_or_reason"
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"])
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    # Hard refusal guardrails
    if args.ward.lower() in {"all", "any"} or args.category.lower() in {"all", "any"}:
        sys.exit("REFUSED: Aggregation across wards or categories is not allowed")

    rows, null_rows = load_dataset(args.input)

    if null_rows:
        print("Detected NULL actual_spend rows:")
        for r in null_rows:
            print(f" - {r['period']} · {r['ward']} · {r['category']} → {r['notes']}")
        print()

    results = compute_growth(
        rows,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type
    )

    write_output(args.output, results)
    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()
