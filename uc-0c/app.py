"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path


REQUIRED_COLUMNS = {
    "period", "ward", "category", "budgeted_amount", "actual_spend", "notes"
}
MOM_FORMULA = "((current_actual_spend - previous_actual_spend) / previous_actual_spend) * 100"
OUTPUT_COLUMNS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend", "growth_type",
    "growth_percent", "formula", "status", "null_reason",
]
ALL_VALUES = {"all", "all wards", "all categories", "*"}


class DatasetError(ValueError):
    """Raised when the supplied dataset cannot be safely used."""


def is_null(value):
    return value is None or value.strip() == ""


def load_dataset(input_path):
    """Read and validate the CSV, reporting every null actual_spend row."""
    try:
        with Path(input_path).open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            if reader.fieldnames is None:
                raise DatasetError("Input CSV has no header row.")
            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise DatasetError(
                    "Input CSV is missing required column(s): " + ", ".join(sorted(missing))
                )
            rows = list(reader)
    except OSError as error:
        raise DatasetError(f"Unable to read input CSV '{input_path}': {error}") from error
    except csv.Error as error:
        raise DatasetError(f"Unable to parse input CSV '{input_path}': {error}") from error

    for row_number, row in enumerate(rows, start=2):
        try:
            datetime.strptime(row["period"], "%Y-%m")
        except ValueError as error:
            raise DatasetError(f"Invalid period at CSV row {row_number}: {row['period']!r}.") from error
        for column in ("ward", "category"):
            if is_null(row[column]):
                raise DatasetError(f"Empty {column} at CSV row {row_number}.")
        if not is_null(row["actual_spend"]):
            try:
                float(row["actual_spend"])
            except ValueError as error:
                raise DatasetError(
                    f"Invalid actual_spend at CSV row {row_number}: {row['actual_spend']!r}."
                ) from error
        try:
            float(row["budgeted_amount"])
        except ValueError as error:
            raise DatasetError(
                f"Invalid budgeted_amount at CSV row {row_number}: {row['budgeted_amount']!r}."
            ) from error

    null_rows = [row for row in rows if is_null(row["actual_spend"])]
    print(f"Null actual_spend rows: {len(null_rows)}", file=sys.stderr)
    for row in null_rows:
        reason = row["notes"].strip() or "No reason supplied in notes"
        print(
            f"FLAGGED NULL: {row['period']} | {row['ward']} | {row['category']} | {reason}",
            file=sys.stderr,
        )
    return rows


def reject_aggregation(value, label):
    if value.strip().casefold() in ALL_VALUES:
        raise DatasetError(
            f"All-{label} aggregation is not allowed. Specify exactly one {label}."
        )


def compute_growth(rows, ward, category, growth_type):
    """Return chronological MoM rows for one exact ward/category without aggregation."""
    if not ward or not ward.strip():
        raise DatasetError("A specific --ward is required; all-ward aggregation is refused.")
    if not category or not category.strip():
        raise DatasetError("A specific --category is required; all-category aggregation is refused.")
    reject_aggregation(ward, "ward")
    reject_aggregation(category, "category")
    if not growth_type:
        raise DatasetError("--growth-type is required. Specify MoM; the calculator will not guess.")
    if growth_type.casefold() != "mom":
        raise DatasetError(f"Unsupported growth type {growth_type!r}. Currently supported: MoM.")

    selected = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not selected:
        raise DatasetError(
            f"No records match ward {ward!r} and category {category!r}; no aggregation was performed."
        )
    selected.sort(key=lambda row: datetime.strptime(row["period"], "%Y-%m"))
    if len({row["period"] for row in selected}) != len(selected):
        raise DatasetError("Duplicate periods found for the requested ward and category.")

    results = []
    previous = None
    for row in selected:
        current_is_null = is_null(row["actual_spend"])
        current = None if current_is_null else float(row["actual_spend"])
        result = {
            "period": row["period"], "ward": ward, "category": category,
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": "" if current_is_null else row["actual_spend"],
            "growth_type": "MoM", "growth_percent": "", "formula": "",
            "status": "", "null_reason": "",
        }
        if previous is None:
            result["status"] = "Not computed: no previous period"
        elif current_is_null:
            result["status"] = "Not computed: null actual_spend"
            result["null_reason"] = row["notes"].strip() or "No reason supplied in notes"
        elif previous["is_null"]:
            result["status"] = "Not computed: previous period actual_spend is null"
            result["null_reason"] = previous["notes"].strip() or "No reason supplied in notes"
        elif previous["value"] == 0:
            result["status"] = "Not computed: previous actual_spend is zero"
        else:
            growth = ((current - previous["value"]) / previous["value"]) * 100
            result["growth_percent"] = f"{growth:.1f}"
            result["formula"] = MOM_FORMULA
            result["status"] = "Computed"
        results.append(result)
        previous = {"is_null": current_is_null, "value": current, "notes": row["notes"]}
    return results


def write_output(output_path, rows):
    try:
        with Path(output_path).open("w", encoding="utf-8", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
    except OSError as error:
        raise DatasetError(f"Unable to write output CSV '{output_path}': {error}") from error


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to the ward budget CSV.")
    parser.add_argument("--ward", required=True, help="One exact ward name.")
    parser.add_argument("--category", required=True, help="One exact category name.")
    parser.add_argument("--growth-type", required=True, help="Growth type; currently MoM only.")
    parser.add_argument("--output", required=True, help="Path for the per-period output CSV.")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        rows = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        write_output(args.output, results)
    except DatasetError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(f"Wrote {len(results)} per-period row(s) to {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
