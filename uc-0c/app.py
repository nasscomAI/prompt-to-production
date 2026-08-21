"""
UC-0C - Budget Growth Calculator

Calculates growth for one ward and one category.
Never aggregates across wards or categories.
"""

import argparse
import csv
import os
from decimal import Decimal, InvalidOperation


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

    with open(
        input_path,
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing))
            )

        rows = list(reader)

    null_rows = []

    for row in rows:
        actual = (row.get("actual_spend") or "").strip()

        if actual == "":
            null_rows.append(row)

    return rows, null_rows


def parse_amount(value):
    """Convert actual spend to Decimal."""

    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None


def compute_growth(rows, ward, category, growth_type):
    """
    Calculate growth for one ward and one category.

    Growth is calculated against the previous month's
    actual spend.

    MoM formula:
        ((current - previous) / previous) * 100

    YoY formula:
        ((current - previous_year) / previous_year) * 100
    """

    if not growth_type:
        raise ValueError(
            "growth_type must be explicitly specified."
        )

    growth_type = growth_type.upper()

    if growth_type not in {"MOM", "YOY"}:
        raise ValueError(
            "growth_type must be either MoM or YoY."
        )

    selected = [
        row
        for row in rows
        if row.get("ward", "").strip() == ward
        and row.get("category", "").strip() == category
    ]

    if not selected:
        raise ValueError(
            f"No rows found for ward '{ward}' "
            f"and category '{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    lookup = {
        row["period"]: row
        for row in selected
    }

    results = []

    for index, row in enumerate(selected):
        period = row["period"].strip()
        current_raw = (row.get("actual_spend") or "").strip()

        current = parse_amount(current_raw)

        # -------------------------------------------------
        # Null current value
        # -------------------------------------------------
        if current_raw == "" or current is None:
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": "NULL",
                    "growth_type": growth_type,
                    "formula": "NOT COMPUTED - actual_spend is NULL",
                    "growth": "NULL",
                    "flag": "NEEDS_REVIEW",
                    "null_reason": row.get("notes", "").strip(),
                }
            )
            continue

        # -------------------------------------------------
        # Find comparison period
        # -------------------------------------------------
        if growth_type == "MOM":
            if index == 0:
                previous = None
                previous_period = ""
            else:
                previous_row = selected[index - 1]
                previous_period = previous_row["period"]
                previous_raw = (
                    previous_row.get("actual_spend") or ""
                ).strip()

                previous = parse_amount(previous_raw)

        else:
            year, month = period.split("-")
            previous_period = f"{int(year) - 1:04d}-{month}"
            previous_row = lookup.get(previous_period)

            if previous_row is None:
                previous = None
            else:
                previous_raw = (
                    previous_row.get("actual_spend") or ""
                ).strip()
                previous = parse_amount(previous_raw)

        # -------------------------------------------------
        # Cannot calculate without comparison value
        # -------------------------------------------------
        if previous is None:
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": str(current),
                    "growth_type": growth_type,
                    "formula": (
                        f"((current - previous) / previous) * 100; "
                        f"comparison period {previous_period or 'N/A'} "
                        f"is unavailable"
                    ),
                    "growth": "NULL",
                    "flag": "NEEDS_REVIEW",
                    "null_reason": (
                        "Previous comparison value is missing."
                    ),
                }
            )
            continue

        # -------------------------------------------------
        # Cannot divide by zero
        # -------------------------------------------------
        if previous == 0:
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": str(current),
                    "growth_type": growth_type,
                    "formula": (
                        f"((current - {previous}) / "
                        f"{previous}) * 100"
                    ),
                    "growth": "NULL",
                    "flag": "NEEDS_REVIEW",
                    "null_reason": (
                        "Previous comparison value is zero."
                    ),
                }
            )
            continue

        growth = ((current - previous) / previous) * Decimal("100")

        formula = (
            f"(({current} - {previous}) / {previous}) * 100"
        )

        results.append(
            {
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": str(current),
                "growth_type": growth_type,
                "formula": formula,
                "growth": f"{growth:.1f}%",
                "flag": "",
                "null_reason": "",
            }
        )

    return results


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exact ward name",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exact category name",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        choices=["MoM", "YoY"],
        help="Growth calculation type",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path",
    )

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

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
        args.output,
        "w",
        newline="",
        encoding="utf-8",
    ) as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"Loaded {len(rows)} rows.")
    print(f"Found {len(null_rows)} null actual_spend rows.")
    print(f"Calculated {len(results)} rows.")
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()