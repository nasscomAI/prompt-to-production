"""
UC-0C — Number That Looks Right

Failure modes addressed:
- Wrong aggregation level
- Silent null handling
- Formula assumption

The program:
1. Loads and validates the CSV.
2. Reports every null actual_spend row.
3. Requires an explicit growth type.
4. Refuses all-ward aggregation.
5. Filters to the requested ward and category.
6. Computes period-over-period growth.
7. Shows the formula used in every output row.
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
    """
    Load and validate the budget CSV.

    Returns:
        list[dict]: validated rows
    """

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {input_path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header row.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        rows = list(reader)

    if not rows:
        raise ValueError("CSV contains no data rows.")

    # Report every null actual_spend before any computation.
    null_rows = []

    for row in rows:
        actual = row["actual_spend"].strip()

        if actual == "":
            null_rows.append(row)

    print(f"Loaded {len(rows)} rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL | {row['period']} | "
            f"{row['ward']} | "
            f"{row['category']} | "
            f"Reason: {row['notes']}"
        )

    return rows


def validate_parameters(ward, category, growth_type):
    """
    Validate analysis parameters.
    """

    if not ward or not ward.strip():
        raise ValueError(
            "Ward must be explicitly specified."
        )

    if not category or not category.strip():
        raise ValueError(
            "Category must be explicitly specified."
        )

    if not growth_type or not growth_type.strip():
        raise ValueError(
            "Growth type must be explicitly specified."
        )

    normalized_growth_type = growth_type.strip().upper()

    if normalized_growth_type != "MOM":
        raise ValueError(
            f"Unsupported growth type '{growth_type}'. "
            "This implementation supports MoM only. "
            "Do not guess a growth formula."
        )

    # Refuse all-ward aggregation.
    if ward.strip().lower() in {
        "all",
        "all wards",
        "all-wards",
        "all ward",
    }:
        raise ValueError(
            "Refusing all-ward aggregation. "
            "Specify one ward."
        )


def compute_growth(rows, ward, category, growth_type):
    """
    Calculate period-over-period growth for one ward and category.
    """

    validate_parameters(
        ward,
        category,
        growth_type
    )

    selected = [
        row for row in rows
        if row["ward"].strip() == ward.strip()
        and row["category"].strip() == category.strip()
    ]

    if not selected:
        raise ValueError(
            f"No rows found for ward '{ward}' "
            f"and category '{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    results = []

    previous_actual = None
    previous_period = None

    for row in selected:

        actual_text = row["actual_spend"].strip()

        # Null actual spend: do not calculate growth.
        if actual_text == "":
            results.append({
                "ward": row["ward"],
                "category": row["category"],
                "period": row["period"],
                "actual_spend": "",
                "growth_type": "MoM",
                "formula": (
                    "NOT COMPUTED — actual_spend is NULL; "
                    f"reason: {row['notes']}"
                ),
                "growth": "",
                "status": "FLAGGED_NULL",
                "null_reason": row["notes"],
            })

            # A null month cannot be used as the previous value.
            previous_actual = None
            previous_period = row["period"]

            continue

        actual = float(actual_text)

        # First period has no previous month.
        if previous_actual is None:
            results.append({
                "ward": row["ward"],
                "category": row["category"],
                "period": row["period"],
                "actual_spend": actual,
                "growth_type": "MoM",
                "formula": (
                    "N/A — no previous valid month available"
                ),
                "growth": "",
                "status": "NO_PREVIOUS_PERIOD",
                "null_reason": "",
            })

        else:
            growth = (
                (actual - previous_actual)
                / previous_actual
            ) * 100

            formula = (
                f"(({actual:.1f} - {previous_actual:.1f}) "
                f"/ {previous_actual:.1f}) × 100"
            )

            results.append({
                "ward": row["ward"],
                "category": row["category"],
                "period": row["period"],
                "actual_spend": actual,
                "growth_type": "MoM",
                "formula": formula,
                "growth": f"{growth:+.1f}%",
                "status": "COMPUTED",
                "null_reason": "",
            })

        previous_actual = actual
        previous_period = row["period"]

    return results


def write_output(results, output_path):
    """
    Write the per-period growth table.
    """

    output_file = Path(output_path)

    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "growth_type",
        "formula",
        "growth",
        "status",
        "null_reason",
    ]

    with output_file.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    print(
        f"Growth output written to: {output_file}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C municipal budget growth analysis"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv"
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Specific ward to analyze"
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Specific budget category to analyze"
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Explicit growth formula, currently MoM"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to growth_output.csv"
    )

    args = parser.parse_args()

    rows = load_dataset(args.input)

    results = compute_growth(
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
        f"Generated {len(results)} per-period rows "
        f"for {args.ward} / {args.category}."
    )


if __name__ == "__main__":
    main()