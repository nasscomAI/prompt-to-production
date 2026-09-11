"""
UC-0C — Number That Looks Right

Calculates growth at the requested ward + category level.
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
    with open(input_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header.")

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
        if row["actual_spend"].strip() == "":
            null_rows.append(row)

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Calculate per-period growth for one ward and one category."""

    if not growth_type:
        raise ValueError(
            "Growth type must be specified. Refusing to guess."
        )

    if growth_type != "MoM":
        raise ValueError(
            "Unsupported growth type. This dataset supports MoM growth."
        )

    if not ward or not category:
        raise ValueError(
            "A specific ward and category are required. "
            "All-ward or cross-category aggregation is not allowed."
        )

    if ward.lower() in {"all", "all wards"}:
        raise ValueError(
            "Refusing all-ward aggregation. A specific ward is required."
        )

    if category.lower() in {"all", "all categories"}:
        raise ValueError(
            "Refusing cross-category aggregation. A specific category is required."
        )

    selected = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    selected.sort(key=lambda row: row["period"])

    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    results = []
    previous_spend = None

    for row in selected:
        period = row["period"]
        actual = row["actual_spend"].strip()
        notes = row["notes"].strip()

        if actual == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "formula": "NOT COMPUTED — actual_spend is NULL",
                "growth": "FLAGGED",
                "null_reason": notes or "No reason provided",
            })

            previous_spend = None
            continue

        current_spend = float(actual)

        if previous_spend is None:
            formula = "N/A — no previous non-null month available"
            growth = "N/A"
        else:
            growth_value = (
                (current_spend - previous_spend)
                / previous_spend
            ) * 100

            formula = (
                f"({current_spend:.1f} - {previous_spend:.1f}) "
                f"/ {previous_spend:.1f} × 100"
            )

            growth = f"{growth_value:+.1f}%"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{current_spend:.1f}",
            "formula": formula,
            "growth": growth,
            "null_reason": "",
        })

        previous_spend = current_spend

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
        "null_reason",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate per-ward, per-category budget growth."
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    print(f"Loaded {len(rows)} rows.")
    print(f"Found {len(null_rows)} NULL actual_spend rows.")

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

    write_output(args.output, results)

    print(f"Growth output written to: {args.output}")


if __name__ == "__main__":
    main()