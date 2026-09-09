"""
UC-0C — Number That Looks Right

Calculates per-month growth for exactly one ward and one category.
"""

import argparse
import csv


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def load_dataset(input_path):
    """Load and validate the budget CSV."""
    with open(input_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        missing = [
            column for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(missing)}"
            )

        rows = list(reader)

    null_rows = []

    for row in rows:
        if not row["actual_spend"].strip():
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row["notes"],
            })

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Compute growth for one ward and one category."""

    if not growth_type:
        raise ValueError(
            "growth_type must be explicitly specified."
        )

    if growth_type != "MoM":
        raise ValueError(
            "Unsupported growth type. This implementation supports MoM only."
        )

    selected = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    selected.sort(key=lambda row: row["period"])

    results = []

    previous_actual = None
    previous_period = None

    for row in selected:

        current_value = row["actual_spend"].strip()

        if not current_value:
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "previous_actual_spend": (
                    "" if previous_actual is None
                    else f"{previous_actual:.2f}"
                ),
                "formula": "NOT_COMPUTED",
                "growth": "NOT_COMPUTED",
                "status": "NULL",
                "null_reason": row["notes"],
            })

            previous_actual = None
            previous_period = row["period"]
            continue

        current_value = float(current_value)

        if previous_actual is None:
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": f"{current_value:.2f}",
                "previous_actual_spend": "",
                "formula": "N/A — first period or previous value is NULL",
                "growth": "N/A",
                "status": "NOT_COMPUTED",
                "null_reason": "",
            })
        else:
            growth = (
                (current_value - previous_actual)
                / previous_actual
            ) * 100

            formula = (
                f"(({current_value:.2f} - {previous_actual:.2f}) "
                f"/ {previous_actual:.2f}) × 100"
            )

            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": f"{current_value:.2f}",
                "previous_actual_spend": f"{previous_actual:.2f}",
                "formula": formula,
                "growth": f"{growth:+.1f}%",
                "status": "COMPUTED",
                "null_reason": "",
            })

        previous_actual = current_value
        previous_period = row["period"]

    return results


def write_output(results, output_path):
    """Write the per-period growth table."""

    fields = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "previous_actual_spend",
        "formula",
        "growth",
        "status",
        "null_reason",
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
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
        help="Path to ward_budget.csv"
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exact ward name"
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exact category name"
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth type, currently supported: MoM"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path"
    )

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    print(f"Loaded {len(rows)} rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for item in null_rows:
        print(
            f"NULL: {item['period']} | "
            f"{item['ward']} | "
            f"{item['category']} | "
            f"Reason: {item['reason']}"
        )

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    write_output(results, args.output)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()