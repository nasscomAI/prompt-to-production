"""
UC-0C app.py — Growth computation for ward budget data.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(path: Path):
    """Load and validate the ward budget dataset."""
    rows = []
    null_rows = []

    with path.open(newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")

        missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append(row)
            rows.append(row)

    return {
        "rows": rows,
        "null_rows": null_rows,
        "columns": reader.fieldnames,
    }


def compute_growth(dataset, ward, category, growth_type):
    """Compute growth for a single ward/category and annotate formula/flags."""
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("growth_type must be 'MoM' or 'YoY'.")

    filtered = [row for row in dataset["rows"] if row["ward"] == ward and row["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")

    sorted_rows = sorted(filtered, key=lambda r: r["period"])
    output = []
    prev_values = {}

    for row in sorted_rows:
        period = row["period"]
        actual = row["actual_spend"].strip()
        notes = row["notes"].strip()

        output_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual if actual != "" else "NULL",
            "formula": "",
            "growth": "",
            "null_reason": notes if actual == "" else "",
        }

        if actual == "":
            output_row["formula"] = "N/A"
            output_row["growth"] = "FLAGGED"
        else:
            current_value = float(actual)
            if growth_type == "MoM":
                prev_period = get_prev_period(period)
            else:
                prev_period = get_yoy_period(period)

            prev_value = prev_values.get(prev_period)
            if prev_value is None:
                output_row["formula"] = "No prior period available"
                output_row["growth"] = "N/A"
            else:
                if prev_value == 0:
                    output_row["formula"] = f"({current_value} - {prev_value}) / {prev_value}"
                    output_row["growth"] = "Inf" if current_value != 0 else "0.0%"
                else:
                    change = (current_value - prev_value) / prev_value * 100
                    output_row["formula"] = f"({current_value} - {prev_value}) / {prev_value} * 100"
                    output_row["growth"] = f"{change:.1f}%"

        prev_values[period] = float(actual) if actual != "" else None
        output.append(output_row)

    return output


def get_prev_period(period: str) -> str:
    year, month = map(int, period.split("-"))
    if month == 1:
        return f"{year-1}-12"
    return f"{year}-{month-1:02d}"


def get_yoy_period(period: str) -> str:
    year, month = map(int, period.split("-"))
    return f"{year-1}-{month:02d}"


def write_output(output_path: Path, rows):
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "null_reason"]
    with output_path.open('w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    dataset = load_dataset(Path(args.input))
    output_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    write_output(Path(args.output), output_rows)
    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()
