"""UC-0C budget growth application.

This script enforces the UC-0C requirements from agents.md and skills.md:
- strict per-ward, per-category analysis only
- explicit null handling before computing growth
- required --growth-type argument with no guessing
- per-row formula shown alongside results
"""

import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

ALLOWED_GROWTH_TYPES = {"MoM", "YoY"}


class DatasetValidationError(ValueError):
    """Raised when the CSV structure or values are invalid."""


class AggregationRequestError(ValueError):
    """Raised when the request would aggregate across wards/categories or guess the growth type."""


def _as_float(value, column_name):
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise DatasetValidationError(
            f"Column '{column_name}' contains a non-numeric value: {value!r}"
        ) from exc


def load_dataset(file_path: str):
    """Load and validate the budget dataset while reporting deliberate null actual_spend rows."""
    if not file_path or not str(file_path).strip():
        raise DatasetValidationError("Input file path is missing. Please provide --input.")

    dataset_path = Path(file_path)
    if not dataset_path.exists() or not dataset_path.is_file():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    rows = []
    null_rows = []

    with dataset_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise DatasetValidationError("Input CSV has no header row.")

        missing_columns = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing_columns:
            raise DatasetValidationError(
                "Input CSV is missing required columns: " + ", ".join(missing_columns)
            )

        for row_number, raw_row in enumerate(reader, start=2):
            normalized = {}
            for column in REQUIRED_COLUMNS:
                normalized[column] = (raw_row.get(column) or "").strip()

            if not normalized["period"]:
                raise DatasetValidationError(f"Row {row_number}: 'period' is required.")
            if not normalized["ward"]:
                raise DatasetValidationError(f"Row {row_number}: 'ward' is required.")
            if not normalized["category"]:
                raise DatasetValidationError(f"Row {row_number}: 'category' is required.")

            budgeted_amount = _as_float(normalized["budgeted_amount"], "budgeted_amount")
            actual_spend = _as_float(normalized["actual_spend"], "actual_spend")

            if budgeted_amount is None:
                raise DatasetValidationError(
                    f"Row {row_number}: 'budgeted_amount' is required and cannot be blank."
                )

            row = {
                "period": normalized["period"],
                "ward": normalized["ward"],
                "category": normalized["category"],
                "budgeted_amount": budgeted_amount,
                "actual_spend": actual_spend,
                "notes": normalized["notes"],
            }
            rows.append(row)

            if actual_spend is None:
                null_rows.append(
                    {
                        "row_index": row_number,
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "note": row["notes"] or "No note supplied",
                    }
                )

    return {"rows": rows, "null_rows": null_rows, "null_count": len(null_rows)}


def compute_growth(dataset, ward, category, growth_type):
    """Compute per-period growth for a specific ward/category pair and flag null actual_spend rows."""
    if not ward or not str(ward).strip():
        raise AggregationRequestError("A specific ward is required. Refusing any all-ward aggregation.")
    if not category or not str(category).strip():
        raise AggregationRequestError("A specific category is required. Refusing any all-category aggregation.")

    normalized_ward = str(ward).strip()
    normalized_category = str(category).strip()
    normalized_growth_type = (growth_type or "").strip()

    if not normalized_growth_type:
        raise AggregationRequestError(
            "Missing required --growth-type. Refuse to guess. Please specify MoM or YoY."
        )

    if normalized_growth_type not in ALLOWED_GROWTH_TYPES:
        raise AggregationRequestError(
            f"Unsupported growth type '{normalized_growth_type}'. Use MoM or YoY."
        )

    if normalized_ward.lower() in {"all", "all wards", "*"}:
        raise AggregationRequestError(
            "Refusing any request to aggregate spend metrics across all wards without explicit instruction."
        )
    if normalized_category.lower() in {"all", "all categories", "*"}:
        raise AggregationRequestError(
            "Refusing any request to aggregate spend metrics across all categories without explicit instruction."
        )

    selected_rows = [
        row for row in dataset["rows"] if row["ward"] == normalized_ward and row["category"] == normalized_category
    ]
    if not selected_rows:
        raise AggregationRequestError(
            f"No data found for ward '{normalized_ward}' and category '{normalized_category}'."
        )

    ordered_rows = sorted(selected_rows, key=lambda row: row["period"])
    null_note_map = {
        (entry["period"], entry["ward"], entry["category"]): entry["note"]
        for entry in dataset["null_rows"]
    }

    output_rows = []
    for index, row in enumerate(ordered_rows):
        period = row["period"]
        actual_spend = row["actual_spend"]
        null_reason = null_note_map.get((period, row["ward"], row["category"]), row["notes"] or "No note supplied")

        if actual_spend is None:
            output_rows.append(
                {
                    "ward": row["ward"],
                    "category": row["category"],
                    "period": period,
                    "actual_spend": "NULL",
                    "growth_type": normalized_growth_type,
                    "growth_result": "NULL",
                    "formula": "NULL actual_spend — not computed. Reason: " + null_reason,
                    "null_flag": "NULL",
                    "null_reason": null_reason,
                }
            )
            continue

        if index == 0:
            growth_result = "N/A"
            formula = "Baseline month — no previous period available for MoM calculation"
        else:
            previous_row = ordered_rows[index - 1]
            previous_actual = previous_row["actual_spend"]
            if previous_actual is None:
                growth_result = "NULL"
                formula = (
                    f"Previous month {previous_row['period']} actual_spend is NULL; "
                    "not computed for this period"
                )
            else:
                growth_value = ((actual_spend - previous_actual) / previous_actual) * 100.0
                growth_result = f"{growth_value:+.1f}%"
                formula = (
                    f"((actual_{period} - actual_{previous_row['period']}) / actual_{previous_row['period']}) * 100 "
                    f"= (({actual_spend} - {previous_actual}) / {previous_actual}) * 100 = {growth_result}"
                )

        output_rows.append(
            {
                "ward": row["ward"],
                "category": row["category"],
                "period": period,
                "actual_spend": f"{actual_spend:.1f}",
                "growth_type": normalized_growth_type,
                "growth_result": growth_result,
                "formula": formula,
                "null_flag": "NOT NULL",
                "null_reason": "",
            }
        )

    return output_rows


def resolve_output_path(output_arg):
    output_path = Path(output_arg)
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path
    return output_path


def write_growth_csv(output_path, rows):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "growth_type",
        "growth_result",
        "formula",
        "null_flag",
        "null_reason",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(
        description="Compute per-ward, per-category spend growth while enforcing UC-0C safety rules."
    )
    parser.add_argument("--input", required=True, help="Budget CSV input path")
    parser.add_argument("--ward", required=True, help="Ward to analyze, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Category to analyze, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=False, help="Growth type, e.g. MoM")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    args = parser.parse_args()

    try:
        dataset_path = str(Path(args.input).resolve()) if Path(args.input).is_absolute() else str((Path(__file__).resolve().parent / args.input))
        dataset = load_dataset(dataset_path)
        growth_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
        output_path = resolve_output_path(args.output)
        write_growth_csv(output_path, growth_rows)
        print(f"Wrote growth output to {output_path}")
    except (FileNotFoundError, DatasetValidationError, AggregationRequestError, ValueError) as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()
