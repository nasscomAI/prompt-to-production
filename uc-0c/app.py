"""
UC-0C — Budget Growth Calculator
"""

import argparse
import csv


def load_dataset(input_path):
    """
    Load and validate the CSV dataset.
    Report all rows where actual_spend is NULL.
    """

    required_columns = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    ]

    rows = []

    with open(input_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for column in required_columns:
            if column not in reader.fieldnames:
                raise ValueError(f"Missing required column: {column}")

        for row in reader:
            rows.append(row)

    # Report NULL rows
    null_rows = [
        row for row in rows
        if row["actual_spend"].strip() == ""
    ]

    print(f"\nFound {len(null_rows)} row(s) with NULL actual_spend:\n")

    for row in null_rows:
        print(
            f"{row['period']} | "
            f"{row['ward']} | "
            f"{row['category']} | "
            f"{row['notes']}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):
    """
    Compute Month-over-Month (MoM) growth
    for one ward and one category only.
    """

    if growth_type.upper() != "MOM":
        raise ValueError(
            "Only MoM growth calculation is supported."
        )

    filtered = [
        row
        for row in rows
        if row["ward"] == ward
        and row["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []
    previous = None

    for row in filtered:

        spend = row["actual_spend"].strip()

        # Handle NULL values
        if spend == "":
            results.append(
                {
                    "period": row["period"],
                    "actual_spend": "",
                    "growth": "",
                    "formula": "",
                    "status": f"NULL ({row['notes']})",
                }
            )
            previous = None
            continue

        spend = float(spend)

        if previous is None:
            growth = "N/A"
            formula = "No previous month"
        else:
            growth_value = (
                (spend - previous) / previous
            ) * 100

            growth = f"{growth_value:.1f}%"

            formula = (
                f"(({spend} - {previous}) / "
                f"{previous}) * 100"
            )

        results.append(
            {
                "period": row["period"],
                "actual_spend": spend,
                "growth": growth,
                "formula": formula,
                "status": "OK",
            }
        )

        previous = spend

    return results


def write_output(results, output_path):
    """
    Write results to CSV.
    """

    fieldnames = [
        "period",
        "actual_spend",
        "growth",
        "formula",
        "status",
    ]

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(results)


def main():

    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input CSV file",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Ward name",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Category name",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth type (MoM)",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV file",
    )

    args = parser.parse_args()

    # Refuse aggregation
    if args.ward.lower() == "all":
        raise ValueError(
            "Aggregation across wards is not allowed."
        )

    if args.category.lower() == "all":
        raise ValueError(
            "Aggregation across categories is not allowed."
        )

    rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(
        results,
        args.output,
    )

    print(f"\nGrowth report written to {args.output}")


if __name__ == "__main__":
    main()