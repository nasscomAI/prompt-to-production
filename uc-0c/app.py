from __future__ import annotations
import argparse

"""
UC-0C budget growth analysis CLI.
Script to load budget CSV, validate requested scope. It flags null actual_spend rows, and writes a per-period growth table
for a single ward and category.
"""  

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def resolve_path(path_str: str, base_dir: Path) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def load_dataset(input_path: Path) -> List[Dict[str, str]]:
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is empty or missing a header row.")

        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        rows: List[Dict[str, str]] = []
        for row in reader:
            normalized = {
                key: (value.strip() if isinstance(value, str) else value)
                for key, value in row.items()
            }
            rows.append(normalized)
        return rows


def previous_period(period: str) -> str:
    year_str, month_str = period.split("-")
    year = int(year_str)
    month = int(month_str)
    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{month - 1:02d}"


def previous_year_period(period: str) -> str:
    year_str, month_str = period.split("-")
    return f"{int(year_str) - 1}-{month_str}"


def format_growth(value: float | None, growth_type: str) -> str:
    if value is None:
        return ""
    if growth_type.upper() == "MOM":
        return f"{value:+.1f}%"
    return f"{value:+.1f}%"


def compute_growth(rows: List[Dict[str, str]], ward: str, category: str, growth_type: str) -> List[Dict[str, str]]:
    growth_type = growth_type.strip().upper()
    if growth_type not in {"MOM", "YOY"}:
        raise ValueError("growth_type must be MoM or YoY")

    scoped_rows = [row for row in rows if row.get("ward") == ward and row.get("category") == category]
    if not scoped_rows:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")

    scoped_rows = sorted(scoped_rows, key=lambda row: row.get("period", ""))
    lookup = {(row.get("period"), row.get("ward"), row.get("category")): row for row in rows}

    results: List[Dict[str, str]] = []
    previous_period_value: float | None = None
    previous_period_label: str | None = None

    for row in scoped_rows:
        period = row.get("period", "")
        actual_raw = (row.get("actual_spend") or "").strip()
        notes = (row.get("notes") or "").strip()

        if not actual_raw:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": row.get("budgeted_amount", ""),
                    "actual_spend": "",
                    "growth_value": "",
                    "formula": f"Not computed: actual spend is null ({notes or 'no notes'})",
                    "null_flag": "true",
                    "notes": notes,
                }
            )
            previous_period_value = None
            previous_period_label = None
            continue

        try:
            current_value = float(actual_raw)
        except ValueError as exc:
            raise ValueError(f"Invalid numeric value for actual_spend at period {period}: {actual_raw}") from exc

        if growth_type == "MOM":
            reference_period = previous_period(period)
            reference_row = lookup.get((reference_period, ward, category))
            reference_value = None
            if reference_row is not None and (reference_row.get("actual_spend") or "").strip():
                try:
                    reference_value = float((reference_row.get("actual_spend") or "").strip())
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid numeric value for actual_spend at period {reference_period}: "
                        f"{reference_row.get('actual_spend')}"
                    ) from exc
            if reference_value is None:
                growth_value = None
                formula = "Not computed: no previous-period actual spend available"
            elif reference_value == 0:
                growth_value = None
                formula = "Not computed: previous-period actual spend was zero"
            else:
                growth_value = ((current_value - reference_value) / reference_value) * 100
                formula = f"({current_value:.1f} - {reference_value:.1f}) / {reference_value:.1f} * 100"
        else:
            reference_period = previous_year_period(period)
            reference_row = lookup.get((reference_period, ward, category))
            reference_value = None
            if reference_row is not None and (reference_row.get("actual_spend") or "").strip():
                try:
                    reference_value = float((reference_row.get("actual_spend") or "").strip())
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid numeric value for actual_spend at period {reference_period}: "
                        f"{reference_row.get('actual_spend')}"
                    ) from exc
            if reference_value is None:
                growth_value = None
                formula = "Not computed: no prior-year actual spend available"
            elif reference_value == 0:
                growth_value = None
                formula = "Not computed: prior-year actual spend was zero"
            else:
                growth_value = ((current_value - reference_value) / reference_value) * 100
                formula = f"({current_value:.1f} - {reference_value:.1f}) / {reference_value:.1f} * 100"

        results.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": row.get("budgeted_amount", ""),
                "actual_spend": actual_raw,
                "growth_value": format_growth(growth_value, growth_type),
                "formula": formula,
                "null_flag": "false",
                "notes": notes,
            }
        )

    return results


def write_output(output_path: Path, rows: List[Dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "period",
                "ward",
                "category",
                "budgeted_amount",
                "actual_spend",
                "growth_value",
                "formula",
                "null_flag",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(description="Compute budget growth for one ward and category")
    parser.add_argument("--input", default=str(base_dir.parent / "data" / "budget" / "ward_budget.csv"), help="Path to the budget CSV")
    parser.add_argument("--ward", default="", help="Ward to analyze")
    parser.add_argument("--category", default="", help="Category to analyze")
    parser.add_argument("--growth-type", default="", help="Growth formula to use: MoM or YoY")
    parser.add_argument("--output", default=str(base_dir / "growth_output.csv"), help="Path to write the growth CSV")
    args = parser.parse_args()

    if not args.ward or not args.category:
        print("Refusing to guess. Please provide both --ward and --category.", file=sys.stderr)
        sys.exit(2)

    if not args.growth_type:
        print("Refusing to guess. Please specify --growth-type as MoM or YoY.", file=sys.stderr)
        sys.exit(2)

    input_path = resolve_path(args.input, base_dir)
    output_path = resolve_path(args.output, base_dir)

    try:
        rows = load_dataset(input_path)
        growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
        write_output(output_path, growth_rows)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Wrote growth report to {output_path}")


if __name__ == "__main__":
    main()
    