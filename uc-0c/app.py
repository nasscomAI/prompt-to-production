"""
UC-0C app.py - ward/category budget growth calculator.

Implements the two skills from skills.md:
- load_dataset: validate the CSV and report null actual_spend rows.
- compute_growth: calculate per-period growth for one ward and one category.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REQUIRED_COLUMNS = ("period", "ward", "category", "budgeted_amount", "actual_spend", "notes")
PERIOD_RE = re.compile(r"^2024-(0[1-9]|1[0-2])$")
SUPPORTED_GROWTH_TYPES = {"MoM"}
MOM_FORMULA = "((current actual_spend - previous period actual_spend) / previous period actual_spend) * 100"


@dataclass(frozen=True)
class BudgetRow:
    period: str
    ward: str
    category: str
    budgeted_amount: float
    actual_spend: float | None
    notes: str


@dataclass(frozen=True)
class NullReportRow:
    period: str
    ward: str
    category: str
    notes: str


@dataclass(frozen=True)
class Dataset:
    rows: tuple[BudgetRow, ...]
    null_report: tuple[NullReportRow, ...]


def normalize_text(value: str) -> str:
    """Normalize dash variants/mojibake for matching and readable output."""
    return value.replace("â€“", "-").replace("–", "-").replace("—", "-").strip()


def match_key(value: str) -> str:
    return normalize_text(value).casefold()


def parse_float(value: str, column: str, row_number: int) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Row {row_number}: {column} must be numeric, got {value!r}") from exc


def load_dataset(input_path: str) -> Dataset:
    """
    Reads the ward budget CSV, validates columns, and reports all null
    actual_spend rows before returning.
    """
    path = Path(input_path)
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Input must be a CSV file: {path}")
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Input path is not a file: {path}")

    rows: list[BudgetRow] = []
    seen_keys: set[tuple[str, str, str]] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is empty or missing a header row.")

        missing_columns = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"Input CSV missing required column(s): {', '.join(missing_columns)}")

        for row_number, raw in enumerate(reader, start=2):
            period = raw["period"].strip()
            if not PERIOD_RE.match(period):
                raise ValueError(f"Row {row_number}: period must be YYYY-MM from 2024-01 to 2024-12.")

            ward = normalize_text(raw["ward"])
            category = normalize_text(raw["category"])
            if not ward:
                raise ValueError(f"Row {row_number}: ward is required.")
            if not category:
                raise ValueError(f"Row {row_number}: category is required.")

            actual_raw = raw["actual_spend"].strip()
            row = BudgetRow(
                period=period,
                ward=ward,
                category=category,
                budgeted_amount=parse_float(raw["budgeted_amount"].strip(), "budgeted_amount", row_number),
                actual_spend=None if actual_raw == "" else parse_float(actual_raw, "actual_spend", row_number),
                notes=normalize_text(raw["notes"]),
            )

            key = (row.period, match_key(row.ward), match_key(row.category))
            if key in seen_keys:
                raise ValueError(f"Duplicate row for period/ward/category: {row.period}, {row.ward}, {row.category}")
            seen_keys.add(key)
            rows.append(row)

    if not rows:
        raise ValueError("Input CSV contains no data rows.")

    null_report = tuple(
        NullReportRow(row.period, row.ward, row.category, row.notes)
        for row in rows
        if row.actual_spend is None
    )
    return Dataset(rows=tuple(rows), null_report=null_report)


def format_amount(value: float | None) -> str:
    return "NULL" if value is None else f"{value:.1f}"


def format_growth(value: float | None) -> str:
    return "NULL" if value is None else f"{value:+.1f}%"


def compute_growth(dataset: Dataset, ward: str, category: str, growth_type: str) -> list[dict[str, str]]:
    """
    Computes growth for one specified ward and category using explicit
    growth_type and returns per-period table rows with formulas shown.
    """
    if not ward or match_key(ward) in {"all", "any", "*"}:
        raise ValueError("Refusing all-ward aggregation: provide one explicit --ward.")
    if not category or match_key(category) in {"all", "any", "*"}:
        raise ValueError("Refusing all-category aggregation: provide one explicit --category.")
    if not growth_type:
        raise ValueError("Missing --growth-type; refuse to guess. Specify one of: MoM.")
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(f"Unsupported --growth-type {growth_type!r}; supported value: MoM.")

    selected = [
        row
        for row in dataset.rows
        if match_key(row.ward) == match_key(ward) and match_key(row.category) == match_key(category)
    ]
    selected.sort(key=lambda row: row.period)

    if not selected:
        raise ValueError(f"No rows found for ward={ward!r} and category={category!r}.")

    output_rows: list[dict[str, str]] = []
    previous: BudgetRow | None = None
    for row in selected:
        comparison_period = previous.period if previous else ""
        comparison_actual = previous.actual_spend if previous else None
        growth: float | None = None

        if row.actual_spend is None:
            status = f"NULL_CURRENT_NOT_COMPUTED: {row.notes}"
        elif previous is None:
            status = "NOT_COMPUTED_FIRST_PERIOD"
        elif previous.actual_spend is None:
            status = f"NULL_COMPARISON_NOT_COMPUTED: {previous.notes}"
        elif previous.actual_spend == 0:
            status = "ZERO_COMPARISON_NOT_COMPUTED"
        else:
            growth = ((row.actual_spend - previous.actual_spend) / previous.actual_spend) * 100
            status = "OK"

        output_rows.append(
            {
                "period": row.period,
                "ward": row.ward,
                "category": row.category,
                "actual_spend": format_amount(row.actual_spend),
                "comparison_period": comparison_period,
                "comparison_actual_spend": format_amount(comparison_actual) if previous else "",
                "growth_type": growth_type,
                "formula": MOM_FORMULA,
                "growth_result": format_growth(growth),
                "status": status,
                "notes": row.notes,
            }
        )
        previous = row

    return output_rows


def print_null_report(null_report: tuple[NullReportRow, ...]) -> None:
    print(f"Null actual_spend rows found before computation: {len(null_report)}")
    for row in null_report:
        reason = row.notes if row.notes else "No note provided"
        print(f"- {row.period} | {row.ward} | {row.category} | {reason}")


def write_output(output_path: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No growth rows produced; refusing to write an empty output file.")
    path = Path(output_path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute per-ward per-category budget growth.")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name; all-ward aggregation is refused.")
    parser.add_argument("--category", required=True, help="Exact category name; all-category aggregation is refused.")
    parser.add_argument("--growth-type", required=True, help="Growth type to compute, e.g. MoM.")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    dataset = load_dataset(args.input)
    print_null_report(dataset.null_report)
    growth_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    write_output(args.output, growth_rows)
    print(f"Wrote {len(growth_rows)} growth rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
