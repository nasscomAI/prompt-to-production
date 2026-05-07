"""
UC-0C app.py — Budget growth calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
import csv
import sys
import re
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

BROAD_REQUEST_TERMS = {
    "all",
    "any",
    "allwards",
    "allcategories",
    "anyward",
    "anycategory",
}

# ---------------------------------------------------------------------------
# Helper functions (mirroring the skills defined in skills.md)
# ---------------------------------------------------------------------------

def load_dataset(path: str):
    """Read the CSV file, validate required columns, and return normalized rows."""
    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        sys.exit(f"Error reading input file: {e}")

    if not rows:
        sys.exit("Input CSV is empty.")

    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0].keys()]
    if missing:
        sys.exit(f"Missing required columns in input CSV: {', '.join(missing)}")

    for row in rows:
        for key, value in row.items():
            row[key] = value.strip() if isinstance(value, str) else value

        actual = row["actual_spend"]
        if actual.upper() in {"", "NULL", "NONE"}:
            row["actual_spend"] = None
        else:
            try:
                row["actual_spend"] = float(actual)
            except ValueError:
                sys.exit(
                    f"Invalid actual_spend value '{actual}' in period {row.get('period')}"
                )

    return rows


def report_nulls(rows):
    """Report null actual_spend rows to stderr."""
    null_rows = [r for r in rows if r["actual_spend"] is None]
    if not null_rows:
        return

    sys.stderr.write(
        f"Flagged {len(null_rows)} null actual_spend rows (will be reported in output):\n"
    )
    for row in null_rows:
        sys.stderr.write(
            f"  period={row['period']}, ward={row['ward']}, "
            f"category={row['category']}, note={row['notes']}\n"
        )


def normalize_key(value: str) -> str:
    """Normalize values for comparison: lowercase and remove non-alphanumeric characters."""
    return re.sub(r"[^0-9A-Za-z]", "", value).lower()


def is_broad_request(value: str) -> bool:
    """Detect broad ward/category requests that must be refused."""
    return normalize_key(value) in BROAD_REQUEST_TERMS


def parse_period(period: str) -> datetime:
    """Parse YYYY-MM period strings."""
    return datetime.strptime(period, "%Y-%m")


def period_minus_one_month(dt: datetime) -> datetime:
    if dt.month == 1:
        return datetime(dt.year - 1, 12, 1)
    return datetime(dt.year, dt.month - 1, 1)


def period_minus_one_year(dt: datetime) -> datetime:
    return datetime(dt.year - 1, dt.month, 1)


# ---------------------------------------------------------------------------
# Core logic (mirroring the skills defined in skills.md)
# ---------------------------------------------------------------------------

def compute_growth(rows, growth_type):
    """Compute growth values and formulas for filtered rows."""
    rows.sort(key=lambda r: parse_period(r["period"]))
    lookup = {parse_period(r["period"]): r for r in rows}

    periods = []
    actual_spends = []
    growth_values = []
    formulas = []
    notes = []

    for row in rows:
        period = row["period"]
        actual = row["actual_spend"]
        periods.append(period)
        actual_spends.append(actual if actual is not None else "")
        notes.append(row["notes"])

        if actual is None:
            growth_values.append("")
            formulas.append("")
            continue

        current_dt = parse_period(period)
        previous_dt = (
            period_minus_one_month(current_dt)
            if growth_type == "MoM"
            else period_minus_one_year(current_dt)
        )

        previous_row = lookup.get(previous_dt)
        if (
            previous_row
            and previous_row["actual_spend"] is not None
            and previous_row["actual_spend"] != 0
        ):
            prev_actual = previous_row["actual_spend"]
            growth = ((actual - prev_actual) / prev_actual) * 100
            growth_values.append(round(growth, 2))
            formulas.append(
                f"{growth_type} growth = (({actual} - {prev_actual}) / {prev_actual}) * 100"
            )
        else:
            growth_values.append("")
            formulas.append("")

    return periods, actual_spends, growth_values, formulas, notes


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Budget growth calculator for municipal infrastructure spend data"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file (e.g., ../data/budget/ward_budget.csv)",
    )
    parser.add_argument(
        "--ward",
        required=True,
        help="Ward name to compute growth for (e.g., 'Ward 1 – Kasba')",
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Category name to compute growth for (e.g., 'Roads & Pothole Repair')",
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=["MoM", "YoY"],
        help="Growth type: MoM (month-over-month) or YoY (year-over-year)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the output CSV file",
    )

    args = parser.parse_args()

    rows = load_dataset(args.input)
    report_nulls(rows)

    if is_broad_request(args.ward) or is_broad_request(args.category):
        sys.exit("Refusing broad request: ward and category must be specific, not All/Any.")

    filtered_rows = [
        row
        for row in rows
        if normalize_key(row["ward"]) == normalize_key(args.ward)
        and normalize_key(row["category"]) == normalize_key(args.category)
    ]

    if not filtered_rows:
        sys.exit(
            "No data found for the requested ward/category. "
            "Ward and category must match dataset values exactly."
        )

    periods, actual_spends, growth_values, formulas, notes = compute_growth(
        filtered_rows, args.growth_type
    )

    output_dir = os.path.dirname(os.path.abspath(args.output))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", newline="") as out_f:
        writer = csv.writer(out_f)
        writer.writerow(
            ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        )
        for period, actual, growth, formula, note in zip(
            periods, actual_spends, growth_values, formulas, notes
        ):
            writer.writerow([
                period,
                args.ward,
                args.category,
                actual,
                growth,
                formula,
                note,
            ])

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()
