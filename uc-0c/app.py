"""
UC-0C app.py — Ward/category growth calculator.

Calculates period-over-period growth only for the explicitly requested
ward, category, and growth type. Null actual_spend values are reported
and never used in a growth calculation.
"""

import argparse
import csv
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

    with open(input_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing))}"
            )

        rows = list(reader)

    null_rows = []

    for row in rows:
        if row["actual_spend"].strip() == "":
            null_rows.append(row)

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Compute growth for one explicitly selected ward and category."""

    if not growth_type:
        raise ValueError(
            "Growth type must be explicitly specified. Refusing to guess."
        )

    growth_type = growth_type.upper()

    if growth_type != "MOM":
        raise ValueError(
            "This implementation supports only explicitly requested MoM growth."
        )

    # Refuse broad aggregation requests.
    if ward.lower() in {"all", "all wards", "any"}:
        raise ValueError(
            "Refusing aggregation across all wards. Specify one ward."
        )

    if category.lower() in {"all", "all categories", "any"}:
        raise ValueError(
            "Refusing aggregation across all categories. Specify one category."
        )

    selected = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    selected.sort(key=lambda row: row["period"])

    results = []
    previous_row = None

    for row in selected:
        current_value = row["actual_spend"].strip()

        # Current value is NULL.
        if current_value == "":
            results.append({
                "ward": ward,
                "category": category,
                "period": row["period"],
                "actual_spend": "",
                "growth_type": "MoM",
                "formula": "NOT COMPUTED — current actual_spend is NULL",
                "growth": "",
                "flag": "NULL",
                "null_reason": row["notes"],
            })

            previous_row = row
            continue

        current_value = float(current_value)

        # No previous month exists.
        if previous_row is None:
            results.append({
                "ward": ward,
                "category": category,
                "period": row["period"],
                "actual_spend": current_value,
                "growth_type": "MoM",
                "formula": "NOT COMPUTED — no previous period",
                "growth": "",
                "flag": "",
                "null_reason": "",
            })

            previous_row = row
            continue

        previous_value = previous_row["actual_spend"].strip()

        # Previous value is NULL.
        if previous_value == "":
            results.append({
                "ward": ward,
                "category": category,
                "period": row["period"],
                "actual_spend": current_value,
                "growth_type": "MoM",
                "formula": (
                    "NOT COMPUTED — previous period actual_spend is NULL"
                ),
                "growth": "",
                "flag": "NULL_PREVIOUS",
                "null_reason": previous_row["notes"],
            })

            previous_row = row
            continue

        previous_value = float(previous_value)

        if previous_value == 0:
            results.append({
                "ward": ward,
                "category": category,
                "period": row["period"],
                "actual_spend": current_value,
                "growth_type": "MoM",
                "formula": "NOT COMPUTED — previous actual_spend is zero",
                "growth": "",
                "flag": "ZERO_PREVIOUS",
                "null_reason": "",
            })
        else:
            growth = ((current_value - previous_value) / previous_value) * 100

            results.append({
                "ward": ward,
                "category": category,
                "period": row["period"],
                "actual_spend": current_value,
                "growth_type": "MoM",
                "formula": (
                    f"(({current_value:g} - {previous_value:g}) "
                    f"/ {previous_value:g}) × 100"
                ),
                "growth": f"{growth:.1f}%",
                "flag": "",
                "null_reason": "",
            })

        previous_row = row

    return results


def write_output(output_path, results):
    """Write the growth results to CSV."""

    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "growth_type",
        "formula",
        "growth",
        "flag",
        "null_reason",
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate ward/category period growth."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward budget CSV.",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exactly one ward to analyze.",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exactly one category to analyze.",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth method. Must be explicitly specified (MoM).",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV.",
    )

    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)

        print(f"Loaded {len(rows)} rows.")
        print(f"Null actual_spend rows found: {len(null_rows)}")

        for row in null_rows:
            print(
                f"NULL: {row['period']} | "
                f"{row['ward']} | "
                f"{row['category']} | "
                f"Reason: {row['notes']}"
            )

        results = compute_growth(
            rows,
            args.ward,
            args.category,
            args.growth_type,
        )

        if not results:
            raise ValueError(
                "No rows found for the requested ward and category."
            )

        write_output(args.output, results)

        print(f"Growth output written to {args.output}")

    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()