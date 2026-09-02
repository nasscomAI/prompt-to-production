"""Deterministic UC-0C budget growth tool."""

import argparse
import csv
import sys


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]
OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "actual_spend",
    "growth_type",
    "formula",
    "growth_percent",
    "status",
    "null_reason",
]


def _is_null(value):
    return value is None or not str(value).strip()


def load_dataset(input_path):
    """Load and validate the CSV, reporting all null actual_spend rows."""
    try:
        with open(input_path, "r", newline="", encoding="utf-8") as input_file:
            reader = csv.DictReader(input_file)
            if reader.fieldnames is None:
                raise ValueError("The CSV has no header row.")

            missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
            if missing:
                raise ValueError("Missing required columns: " + ", ".join(missing))

            rows = []
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(f"Malformed CSV row {row_number}: too many fields.")
                if any(row.get(column) is None for column in REQUIRED_COLUMNS):
                    raise ValueError(f"Malformed CSV row {row_number}: missing fields.")
                rows.append(row)
    except (OSError, csv.Error) as error:
        raise ValueError(f"Unable to read CSV: {error}") from error

    null_rows = [row for row in rows if _is_null(row["actual_spend"])]
    print(f"Detected null actual_spend rows: {len(null_rows)}", file=sys.stderr)
    for row in null_rows:
        print(
            f"NULL period={row['period']} ward={row['ward']} "
            f"category={row['category']} reason={row['notes']}",
            file=sys.stderr,
        )
    return rows


def _parse_spend(row):
    if _is_null(row["actual_spend"]):
        return None
    try:
        return float(row["actual_spend"])
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Invalid actual_spend for period {row['period']}, "
            f"ward {row['ward']}, category {row['category']}."
        ) from error


def compute_growth(rows, ward, category, growth_type):
    """Return the requested ward/category series with deterministic MoM growth."""
    if not growth_type:
        raise ValueError("--growth-type is required; specify MoM.")
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth type: {growth_type}. Supported type: MoM.")
    if ward is None or not str(ward).strip():
        raise ValueError("--ward is required and must match a CSV value exactly.")
    if category is None or not str(category).strip():
        raise ValueError("--category is required and must match a CSV value exactly.")

    wards = {row["ward"] for row in rows}
    categories = {row["category"] for row in rows}
    if ward not in wards:
        raise ValueError(f"Invalid ward: {ward}")
    if category not in categories:
        raise ValueError(f"Invalid category: {category}")

    selected = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not selected:
        raise ValueError(f"No rows found for ward {ward} and category {category}.")
    selected.sort(key=lambda row: row["period"])

    result = []
    previous_row = None
    previous_spend = None
    for row in selected:
        current_spend = _parse_spend(row)
        output = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": row["actual_spend"],
            "growth_type": growth_type,
            "formula": "",
            "growth_percent": "",
            "status": "",
            "null_reason": "",
        }

        if previous_row is None:
            output["formula"] = "N/A - no previous period"
            output["status"] = "NOT_COMPUTED"
        elif current_spend is None or previous_spend is None:
            output["formula"] = "NOT_COMPUTED - current or previous actual_spend is null"
            output["status"] = "FLAGGED_NULL"
            if current_spend is None:
                output["null_reason"] = row["notes"]
            else:
                output["null_reason"] = previous_row["notes"]
        else:
            growth = ((current_spend - previous_spend) / previous_spend) * 100
            output["formula"] = (
                f"(({row['actual_spend']} - {previous_row['actual_spend']}) / "
                f"{previous_row['actual_spend']}) * 100"
            )
            output["growth_percent"] = f"{growth:.1f}"
            output["status"] = "CALCULATED"

        result.append(output)
        previous_row = row
        previous_spend = current_spend
    return result


def write_output(output_path, results):
    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Tool")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, help="Supported growth type: MoM")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        write_output(args.output, results)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
