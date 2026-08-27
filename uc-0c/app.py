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
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a CSV input file, got: {path.name}")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")

        missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing_columns:
            missing_text = ", ".join(sorted(missing_columns))
            raise ValueError(f"Input CSV is missing required columns: {missing_text}")

        rows = []
        null_rows = []

        for index, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items()}

            try:
                budgeted_amount = float(row["budgeted_amount"])
            except ValueError as exc:
                raise ValueError(
                    f"Invalid budgeted_amount at CSV line {index}: {row['budgeted_amount']}"
                ) from exc

            actual_spend = None
            if row["actual_spend"]:
                try:
                    actual_spend = float(row["actual_spend"])
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid actual_spend at CSV line {index}: {row['actual_spend']}"
                    ) from exc

            parsed = {
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted_amount,
                "actual_spend": actual_spend,
                "notes": row["notes"],
            }
            rows.append(parsed)

            if actual_spend is None:
                null_rows.append(parsed)

    return {
        "rows": rows,
        "wards": sorted({row["ward"] for row in rows}),
        "categories": sorted({row["category"] for row in rows}),
        "null_rows": null_rows,
    }


def validate_request(dataset, ward, category, growth_type):
    if not ward or ward.strip().lower() in {"all", "*"}:
        raise ValueError(
            "Refused: analysis must be restricted to one explicit ward; all-ward aggregation is not allowed."
        )
    if not category or category.strip().lower() in {"all", "*"}:
        raise ValueError(
            "Refused: analysis must be restricted to one explicit category; cross-category aggregation is not allowed."
        )
    if not growth_type:
        raise ValueError("Refused: --growth-type is required; the system will not guess a formula.")
    if growth_type != "MoM":
        raise ValueError(
            f"Refused: unsupported growth type '{growth_type}'. Use exactly 'MoM' for this use case."
        )
    if ward not in dataset["wards"]:
        raise ValueError(f"Unknown ward: {ward}")
    if category not in dataset["categories"]:
        raise ValueError(f"Unknown category: {category}")


def format_amount(value):
    if value is None:
        return "NULL"
    return f"{value:.1f}"


def format_growth(value):
    if value is None:
        return "NULL"
    return f"{value:+.1f}%"


def compute_growth(dataset, ward, category, growth_type):
    validate_request(dataset, ward, category, growth_type)

    scoped_rows = [
        row for row in dataset["rows"] if row["ward"] == ward and row["category"] == category
    ]
    scoped_rows.sort(key=lambda row: row["period"])

    if not scoped_rows:
        raise ValueError("No rows matched the requested ward and category.")

    output_rows = []
    previous_row = None

    for row in scoped_rows:
        actual_spend = row["actual_spend"]
        formula = ""
        growth_percent = None
        status = "ok"
        details = ""

        if actual_spend is None:
            status = "flagged_null_current"
            details = f"Null actual_spend for this period: {row['notes']}"
        elif previous_row is None:
            status = "baseline_no_previous_period"
            details = "First period in the series; MoM growth cannot be computed without a previous month."
        elif previous_row["actual_spend"] is None:
            status = "flagged_null_previous"
            details = (
                "Previous period actual_spend is null; growth not computed. "
                f"Previous null reason: {previous_row['notes']}"
            )
        elif previous_row["actual_spend"] == 0:
            status = "flagged_zero_previous"
            details = "Previous period actual_spend is zero; MoM growth would be undefined."
            formula = (
                f"(({format_amount(actual_spend)} - {format_amount(previous_row['actual_spend'])}) / "
                f"{format_amount(previous_row['actual_spend'])}) * 100"
            )
        else:
            formula = (
                f"(({format_amount(actual_spend)} - {format_amount(previous_row['actual_spend'])}) / "
                f"{format_amount(previous_row['actual_spend'])}) * 100"
            )
            growth_percent = ((actual_spend - previous_row["actual_spend"]) / previous_row["actual_spend"]) * 100
            details = "Computed from current and previous month actual_spend values."

        output_rows.append(
            {
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": format_amount(actual_spend),
                "growth_type": growth_type,
                "formula": formula or "N/A",
                "growth_percent": format_growth(growth_percent),
                "status": status,
                "details": details,
            }
        )
        previous_row = row

    return output_rows


def write_output(output_path, rows):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_percent",
        "status",
        "details",
    ]
    path = Path(output_path)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute ward-level budget growth without cross-ward aggregation."
    )
    parser.add_argument("--input", required=True, help="Path to the ward budget CSV file.")
    parser.add_argument("--ward", required=True, help="Exact ward name.")
    parser.add_argument("--category", required=True, help="Exact category name.")
    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth formula to use. This implementation supports exactly 'MoM'.",
    )
    parser.add_argument("--output", required=True, help="Path to the output CSV file.")
    return parser.parse_args()


def main():
    args = parse_args()
    dataset = load_dataset(args.input)
    output_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    write_output(args.output, output_rows)


if __name__ == "__main__":
    main()
