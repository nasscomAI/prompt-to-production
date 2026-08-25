"""
UC-0C - Number That Looks Right

Calculates growth for one explicitly requested ward and category.
"""

import argparse
import csv
import os
import sys


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path):
    """Load and validate the budget CSV."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header row.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing:
            raise ValueError(
                "Missing required columns: " + ", ".join(sorted(missing))
            )

        rows = list(reader)

    null_rows = []

    for row in rows:
        actual = row["actual_spend"].strip()

        if actual == "":
            null_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": row["notes"],
                }
            )

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Compute growth for one ward and one category."""

    if not growth_type:
        raise ValueError(
            "Growth type must be explicitly specified. "
            "Use --growth-type MoM."
        )

    if growth_type.upper() != "MOM":
        raise ValueError(
            f"Unsupported growth type: {growth_type}. "
            "Only MoM is supported."
        )

    # Filter to exactly one ward and one category.
    selected = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    # Sort chronologically.
    selected.sort(key=lambda row: row["period"])

    results = []

    previous_actual = None
    previous_period = None

    for row in selected:
        period = row["period"]
        actual_text = row["actual_spend"].strip()
        notes = row["notes"].strip()

        if actual_text == "":
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "",
                    "formula": "NOT COMPUTED - current actual_spend is NULL",
                    "growth": "",
                    "status": "FLAGGED",
                    "null_reason": notes,
                }
            )

            # A null value cannot become the previous value for computation.
            previous_actual = None
            previous_period = period
            continue

        try:
            actual = float(actual_text)
        except ValueError:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual_text,
                    "formula": "NOT COMPUTED - invalid actual_spend",
                    "growth": "",
                    "status": "FLAGGED",
                    "null_reason": notes,
                }
            )

            previous_actual = None
            previous_period = period
            continue

        if previous_actual is None:
            formula = "NOT COMPUTED - no valid previous actual_spend"
            growth = ""
            status = "NOT_COMPUTED"
        elif previous_actual == 0:
            formula = (
                f"NOT COMPUTED - previous actual_spend for {previous_period} "
                "is zero"
            )
            growth = ""
            status = "FLAGGED"
        else:
            growth_value = ((actual - previous_actual) / previous_actual) * 100

            formula = (
                f"(({actual:.2f} - {previous_actual:.2f}) "
                f"/ {previous_actual:.2f}) * 100"
            )

            growth = f"{growth_value:+.1f}%"
            status = "COMPUTED"

        results.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual:.2f}",
                "formula": formula,
                "growth": growth,
                "status": status,
                "null_reason": "",
            }
        )

        previous_actual = actual
        previous_period = period

    return results


def write_output(output_path, results):
    """Write the growth results to CSV."""
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "formula",
        "growth",
        "status",
        "null_reason",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward/category growth calculator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exactly one ward to analyze",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exactly one category to analyze",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth type. Currently supported: MoM",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path",
    )

    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)

        print(f"Loaded {len(rows)} rows.")

        print(f"Found {len(null_rows)} null actual_spend rows.")

        for item in null_rows:
            print(
                f"NULL: {item['period']} | "
                f"{item['ward']} | "
                f"{item['category']} | "
                f"{item['reason']}"
            )

        results = compute_growth(
            rows,
            args.ward,
            args.category,
            args.growth_type,
        )

        write_output(args.output, results)

        print(f"Done. Results written to {args.output}")

    except (FileNotFoundError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()