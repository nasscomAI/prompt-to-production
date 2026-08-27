"""
UC-0C app.py — Ward/category growth calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import re
from pathlib import Path

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]
VALID_GROWTH_TYPES = {"MOM": "MoM", "YOY": "YoY"}
PERIOD_PATTERN = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")


def load_dataset(input_path: str):
    """Read and validate the ward budget CSV, reporting null actual_spend rows."""
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {input_path}")

    rows = []
    null_rows = []

    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("Input CSV file is empty or malformed.")

        missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        for line_number, raw_row in enumerate(reader, start=2):
            period = raw_row["period"].strip()
            ward = raw_row["ward"].strip()
            category = raw_row["category"].strip()
            budgeted_amount = raw_row["budgeted_amount"].strip()
            actual_spend = raw_row["actual_spend"].strip()
            notes = raw_row["notes"].strip()

            if not PERIOD_PATTERN.match(period):
                raise ValueError(f"Invalid period format at line {line_number}: {period}")

            try:
                budget_value = float(budgeted_amount)
            except ValueError as error:
                raise ValueError(f"Invalid budgeted_amount at line {line_number}: {budgeted_amount}") from error

            if actual_spend == "":
                actual_value = None
                null_rows.append({
                    "line": line_number,
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "notes": notes,
                })
            else:
                try:
                    actual_value = float(actual_spend)
                except ValueError as error:
                    raise ValueError(f"Invalid actual_spend at line {line_number}: {actual_spend}") from error

            rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budget_value,
                "actual_spend": actual_value,
                "notes": notes,
            })

    if null_rows:
        print(f"Found {len(null_rows)} rows with null actual_spend:")
        for null_row in null_rows:
            print(
                f"  line {null_row['line']}: {null_row['period']} | {null_row['ward']} | {null_row['category']} | reason={null_row['notes']}"
            )

    return rows, null_rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """Compute per-period growth for a single ward and category with formula transparency."""
    if not growth_type:
        raise ValueError("--growth-type is required and must be either MoM or YoY.")

    growth_key = growth_type.strip().upper()
    if growth_key not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"Unsupported growth_type '{growth_type}'. Supported values: {', '.join(VALID_GROWTH_TYPES.values())}."
        )

    growth_type = VALID_GROWTH_TYPES[growth_key]

    filtered = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not filtered:
        available_wards = sorted({row["ward"] for row in rows})
        available_categories = sorted({row["category"] for row in rows})
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'. "
            f"Available wards: {available_wards}. Available categories: {available_categories}."
        )

    filtered.sort(key=lambda row: row["period"])
    results = []
    period_index = {row["period"]: row for row in filtered}

    for index, row in enumerate(filtered):
        previous_period = None
        previous_actual = None

        if growth_type == "MoM":
            previous_period = filtered[index - 1]["period"] if index > 0 else None
            previous_actual = filtered[index - 1]["actual_spend"] if index > 0 else None
        else:  # YoY
            year, month = map(int, row["period"].split("-"))
            previous_year = year - 1
            previous_period = f"{previous_year:04d}-{month:02d}"
            previous_row = period_index.get(previous_period)
            previous_actual = previous_row["actual_spend"] if previous_row is not None else None

        formula = ""
        growth_pct = ""
        status = "COMPUTED"
        notes = row["notes"]

        if row["actual_spend"] is None:
            status = "NULL_ACTUAL"
            notes = notes or "Actual spend is missing for this period."
        elif previous_actual is None:
            status = "NO_BASELINE"
            notes = notes or "No valid baseline actual spend available for growth computation."
            formula = f"{growth_type} growth requires a prior period actual spend."
        elif previous_actual == 0:
            status = "DIV_BY_ZERO"
            notes = notes or "Previous period actual spend is zero, growth cannot be computed."
            formula = "Previous actual_spend is zero; growth is undefined."
        else:
            current = row["actual_spend"]
            previous = previous_actual
            if growth_type == "MoM":
                change = current - previous
            else:
                change = current - previous
            growth_value = (change / previous) * 100
            growth_pct = f"{growth_value:+.1f}%"
            formula = f"(({current} - {previous}) / {previous}) * 100"

        results.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": "NULL" if row["actual_spend"] is None else f"{row['actual_spend']:.1f}",
            "previous_period": previous_period or "",
            "previous_actual_spend": "NULL" if previous_actual is None else f"{previous_actual:.1f}",
            "growth_type": growth_type,
            "growth_pct": growth_pct,
            "formula": formula,
            "status": status,
            "notes": notes,
        })

    return results


def write_output(output_path: str, results):
    path = Path(output_path)
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        fieldnames = [
            "period",
            "ward",
            "category",
            "actual_spend",
            "previous_period",
            "previous_actual_spend",
            "growth_type",
            "growth_pct",
            "formula",
            "status",
            "notes",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="UC-0C ward/category growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category name to filter")
    parser.add_argument("--growth-type", required=True, help="Growth type, e.g. MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, _ = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, results)
    print(f"Growth output written to {args.output}")


if __name__ == "__main__":
    main()
