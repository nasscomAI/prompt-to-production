"""
UC-0C — Infrastructure Spend Growth Analyzer

Calculates month-over-month growth in actual infrastructure
spend for a selected ward and category.

Input:
    data/budget/ward_budget.csv

Required columns:
    period
    ward
    category
    actual_spend

Output:
    growth_output.csv
"""

import argparse
import csv
import os


def normalize_text(value):
    """Normalize text for reliable comparisons."""
    return " ".join(value.strip().lower().split())


def load_budget_data(input_path):
    """Load and validate the ward budget CSV."""

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    with open(
        input_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        rows = list(reader)

        required_columns = {
            "period",
            "ward",
            "category",
            "actual_spend"
        }

        actual_columns = set(reader.fieldnames or [])

        missing = required_columns - actual_columns

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing))
            )

    if not rows:
        raise ValueError("Budget CSV is empty.")

    return rows


def calculate_growth(rows, ward, category, growth_type):
    """Calculate month-over-month growth."""

    if normalize_text(growth_type) not in {
        "mom",
        "month-over-month",
        "month_over_month"
    }:
        raise ValueError(
            "Unsupported growth type. "
            "Use 'mom' or 'month-over-month'."
        )

    requested_ward = normalize_text(ward)
    requested_category = normalize_text(category)

    matching_rows = []

    for row in rows:

        row_ward = normalize_text(row["ward"])
        row_category = normalize_text(row["category"])

        # Allow commands such as --ward "Ward 1"
        # to match "Ward 1 – Kasba".
        ward_matches = (
            row_ward == requested_ward
            or row_ward.startswith(requested_ward)
        )

        category_matches = (
            row_category == requested_category
        )

        if not ward_matches:
            continue

        if not category_matches:
            continue

        actual_spend = row["actual_spend"].strip()

        # Missing actual-spend values are not usable
        # for a numerical growth calculation.
        if actual_spend == "":
            continue

        try:
            spend = float(actual_spend)
        except ValueError:
            raise ValueError(
                f"Invalid actual_spend value in "
                f"period '{row['period']}': "
                f"{actual_spend}"
            )

        matching_rows.append({
            "period": row["period"].strip(),
            "ward": row["ward"].strip(),
            "category": row["category"].strip(),
            "actual_spend": spend
        })

    if len(matching_rows) < 2:
        raise ValueError(
            "At least two valid monthly records are required "
            "for the selected ward and category."
        )

    # The source uses YYYY-MM periods, so normal string
    # sorting gives chronological order.
    matching_rows.sort(
        key=lambda row: row["period"]
    )

    results = []

    for previous, current in zip(
        matching_rows,
        matching_rows[1:]
    ):

        previous_spend = previous["actual_spend"]
        current_spend = current["actual_spend"]

        if previous_spend == 0:
            growth = "N/A"
        else:
            growth = round(
                (
                    (current_spend - previous_spend)
                    / previous_spend
                ) * 100,
                2
            )

        results.append({
            "ward": current["ward"],
            "category": current["category"],
            "previous_period": previous["period"],
            "current_period": current["period"],
            "previous_actual_spend": previous_spend,
            "current_actual_spend": current_spend,
            "growth_percent": growth
        })

    return results


def write_output(results, output_path):
    """Write calculated growth results to CSV."""

    output_directory = os.path.dirname(output_path)

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    fieldnames = [
        "ward",
        "category",
        "previous_period",
        "current_period",
        "previous_actual_spend",
        "current_actual_spend",
        "growth_percent"
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for result in results:
            writer.writerow(result)


def main():
    """Command-line entry point."""

    parser = argparse.ArgumentParser(
        description=(
            "UC-0C Infrastructure Spend "
            "Growth Analyzer"
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV"
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Ward to analyze"
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Infrastructure category to analyze"
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth type, e.g. mom"
    )

    args = parser.parse_args()

    rows = load_budget_data(args.input)

    results = calculate_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    write_output(
        results,
        args.output
    )

    print(
        f"Done. Results written to {args.output}"
    )

    print(
        f"Rows written: {len(results)}"
    )


if __name__ == "__main__":
    main()