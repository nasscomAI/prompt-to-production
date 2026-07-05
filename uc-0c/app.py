"""
UC-0C - Ward/category budget growth calculator.
"""

import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "previous_period",
    "previous_actual_spend",
    "growth_type",
    "growth",
    "formula",
    "notes",
]


def load_dataset(input_path: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Read and validate the budget CSV, returning rows and all null actual_spend rows."""
    path = Path(input_path)
    if not path.exists():
        raise ValueError(f"Input file not found: {input_path}")

    with path.open(newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV must contain a header row.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Input CSV is missing required columns: {missing}")

        rows = []
        null_rows = []
        for row_number, row in enumerate(reader, start=2):
            clean_row = {column: (row.get(column) or "").strip() for column in reader.fieldnames}
            clean_row["_row_number"] = str(row_number)
            rows.append(clean_row)
            if clean_row["actual_spend"] == "":
                null_rows.append(clean_row)

    if not rows:
        raise ValueError("Input CSV contains no data rows.")

    return rows, null_rows


def parse_amount(value: str, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not numeric: {value!r}") from exc


def format_growth(value: float) -> str:
    return f"{value:+.1f}%"


def compute_growth(
    rows: list[dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict[str, str]]:
    """Return a per-period table for one ward and one category."""
    if not growth_type:
        raise ValueError("--growth-type is required; refusing to guess the formula.")
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth type {growth_type!r}; only MoM is supported.")

    filtered_rows = [
        row for row in rows
        if row.get("ward") == ward and row.get("category") == category
    ]
    if not filtered_rows:
        raise ValueError(f"No rows found for ward {ward!r} and category {category!r}.")

    filtered_rows.sort(key=lambda row: row["period"])

    output_rows = []
    previous_row: dict[str, str] | None = None

    for row in filtered_rows:
        output_row = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": row["actual_spend"],
            "previous_period": previous_row["period"] if previous_row else "",
            "previous_actual_spend": previous_row["actual_spend"] if previous_row else "",
            "growth_type": growth_type,
            "growth": "NOT_COMPUTED",
            "formula": "",
            "notes": row.get("notes", ""),
        }

        if row["actual_spend"] == "":
            output_row["notes"] = row.get("notes") or "actual_spend is null"
            output_rows.append(output_row)
            previous_row = row
            continue

        if previous_row is None:
            output_row["notes"] = "No previous period for MoM comparison"
            output_rows.append(output_row)
            previous_row = row
            continue

        if previous_row["actual_spend"] == "":
            previous_note = previous_row.get("notes") or "actual_spend is null"
            output_row["notes"] = f"Previous period {previous_row['period']} actual_spend is null: {previous_note}"
            output_rows.append(output_row)
            previous_row = row
            continue

        current = parse_amount(row["actual_spend"], f"{row['period']} actual_spend")
        previous = parse_amount(previous_row["actual_spend"], f"{previous_row['period']} actual_spend")
        if previous == 0:
            output_row["notes"] = f"Previous period {previous_row['period']} actual_spend is zero"
            output_rows.append(output_row)
            previous_row = row
            continue

        growth = ((current - previous) / previous) * 100
        output_row["growth"] = format_growth(growth)
        output_row["formula"] = f"(({current:.1f} - {previous:.1f}) / {previous:.1f}) * 100"
        output_rows.append(output_row)
        previous_row = row

    return output_rows


def write_output(rows: list[dict[str, str]], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="UC-0C budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward to filter exactly")
    parser.add_argument("--category", required=True, help="Category to filter exactly")
    parser.add_argument("--growth-type", required=True, help="Growth type; must be MoM")
    parser.add_argument("--output", required=True, help="Output CSV path")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)
        output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
        write_output(output_rows, args.output)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Done. Growth output written to {args.output}")
    print(f"Detected {len(null_rows)} null actual_spend row(s) before computing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
