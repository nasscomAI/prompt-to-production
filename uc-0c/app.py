"""
UC-0C — Number That Looks Right

Source-grounded ward/category budget growth calculator.
"""

import argparse
import csv
from pathlib import Path


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
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Dataset has no header row.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        rows = list(reader)

    null_rows = []

    for row in rows:
        if row["actual_spend"].strip() == "":
            null_rows.append(row)

    print(f"Loaded {len(rows)} data rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | "
            f"{row['ward']} | "
            f"{row['category']} | "
            f"Reason: {row['notes']}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):
    """Compute growth for exactly one ward and one category."""

    if not ward:
        raise ValueError("Ward must be specified.")

    if not category:
        raise ValueError("Category must be specified.")

    if not growth_type:
        raise ValueError(
            "Growth type must be specified. Refusing to guess."
        )

    if growth_type != "MoM":
        raise ValueError(
            f"Unsupported growth type: {growth_type}. "
            "This application currently supports only MoM."
        )

    if ward.upper() == "ALL" or category.upper() == "ALL":
        raise ValueError(
            "REFUSED: All-ward or cross-category aggregation is not "
            "permitted. Please specify exactly one ward and one category."
        )

    selected_rows = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not selected_rows:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    selected_rows.sort(key=lambda row: row["period"])

    results = []
    previous_spend = None

    for row in selected_rows:
        current_raw = row["actual_spend"].strip()

        if current_raw == "":
            results.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": "",
                    "formula": "",
                    "growth": "",
                    "status": "NULL — not computed",
                    "reason": row["notes"],
                }
            )

            previous_spend = None
            continue

        current_spend = float(current_raw)

        if previous_spend is None:
            results.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": current_spend,
                    "formula": "N/A — no previous month",
                    "growth": "",
                    "status": "BASELINE — not computed",
                    "reason": "",
                }
            )
        else:
            growth = (
                (current_spend - previous_spend)
                / previous_spend
                * 100
            )

            formula = (
                f"({current_spend:.1f} - {previous_spend:.1f}) "
                f"/ {previous_spend:.1f} * 100"
            )

            results.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": current_spend,
                    "formula": formula,
                    "growth": f"{growth:.1f}%",
                    "status": "COMPUTED",
                    "reason": "",
                }
            )

        previous_spend = current_spend

    return results


def write_output(results, output_path):
    """Write the per-period growth table to CSV."""

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "formula",
        "growth",
        "status",
        "reason",
    ]

    path = Path(output_path)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Output written to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate ward/category budget growth."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the ward budget CSV.",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exactly one ward to analyse.",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exactly one category to analyse.",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth type. Currently supported: MoM.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the output CSV.",
    )

    args = parser.parse_args()

    rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(results, args.output)


if __name__ == "__main__":
    main()
