"""Compute explicit per-ward, per-category spend growth with null auditing."""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


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
    "actual_spend",
    "growth_type",
    "comparison_period",
    "comparison_actual_spend",
    "growth_percent",
    "formula",
    "status",
    "null_reason",
]


class RefusalError(ValueError):
    """Raised when the contract requires refusing instead of guessing."""


@dataclass(frozen=True)
class BudgetRow:
    period: str
    ward: str
    category: str
    budgeted_amount: float
    actual_spend: float | None
    notes: str


def _parse_number(value: str, field: str, line: int, nullable: bool = False) -> float | None:
    value = value.strip()
    if nullable and not value:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise RefusalError(f"line {line}: {field} must be numeric, got {value!r}") from exc


def load_dataset(path: str | Path) -> tuple[list[BudgetRow], list[BudgetRow]]:
    """Validate and load the CSV, returning rows and all null-actual rows."""
    source = Path(path)
    try:
        handle = source.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise RefusalError(f"cannot read input CSV {source}: {exc}") from exc

    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RefusalError("input CSV is empty or has no header")
        missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames))
        if missing:
            raise RefusalError(f"input CSV is missing required columns: {', '.join(missing)}")

        rows: list[BudgetRow] = []
        seen: set[tuple[str, str, str]] = set()
        for line, raw in enumerate(reader, start=2):
            period = raw["period"].strip()
            try:
                datetime.strptime(period, "%Y-%m")
            except ValueError as exc:
                raise RefusalError(f"line {line}: invalid period {period!r}; expected YYYY-MM") from exc

            ward = raw["ward"].strip()
            category = raw["category"].strip()
            if not ward or not category:
                raise RefusalError(f"line {line}: ward and category must not be blank")
            key = (ward, category, period)
            if key in seen:
                raise RefusalError(
                    f"line {line}: duplicate ward/category/period row: {ward!r}, {category!r}, {period}"
                )
            seen.add(key)

            actual = _parse_number(raw["actual_spend"], "actual_spend", line, nullable=True)
            notes = raw["notes"].strip()
            if actual is None and not notes:
                raise RefusalError(f"line {line}: null actual_spend must have a reason in notes")
            rows.append(
                BudgetRow(
                    period=period,
                    ward=ward,
                    category=category,
                    budgeted_amount=float(_parse_number(raw["budgeted_amount"], "budgeted_amount", line)),
                    actual_spend=actual,
                    notes=notes,
                )
            )

    if not rows:
        raise RefusalError("input CSV contains no data rows")
    rows.sort(key=lambda row: (row.period, row.ward, row.category))
    null_rows = [row for row in rows if row.actual_spend is None]
    return rows, null_rows


def _shift_period(period: str, months: int) -> str:
    parsed = datetime.strptime(period, "%Y-%m")
    absolute_month = parsed.year * 12 + parsed.month - 1 + months
    year, zero_based_month = divmod(absolute_month, 12)
    return f"{year:04d}-{zero_based_month + 1:02d}"


def _require_exact_selection(value: str | None, label: str, available: Iterable[str]) -> str:
    if value is None or not value.strip():
        raise RefusalError(f"--{label} is required; aggregation is not allowed")
    selection = value.strip()
    if selection.casefold() in {"all", "any", "*", "all wards", "all categories"}:
        raise RefusalError(f"all-{label} aggregation is not allowed; select exactly one {label}")
    choices = set(available)
    if selection not in choices:
        raise RefusalError(
            f"unknown {label} {selection!r}; available values: {', '.join(sorted(choices))}"
        )
    return selection


def compute_growth(
    rows: list[BudgetRow],
    ward: str | None,
    category: str | None,
    growth_type: str | None,
) -> list[dict[str, object]]:
    """Return growth rows for one exact ward-category pair."""
    ward = _require_exact_selection(ward, "ward", (row.ward for row in rows))
    category = _require_exact_selection(category, "category", (row.category for row in rows))
    if growth_type is None or not growth_type.strip():
        raise RefusalError("--growth-type is required; choose MoM or YoY")
    normalized = growth_type.strip().casefold()
    if normalized not in {"mom", "yoy"}:
        raise RefusalError(f"unsupported growth type {growth_type!r}; choose MoM or YoY")
    growth_label = "MoM" if normalized == "mom" else "YoY"
    offset = -1 if growth_label == "MoM" else -12

    selected = [row for row in rows if row.ward == ward and row.category == category]
    if not selected:
        raise RefusalError(f"no rows found for ward {ward!r} and category {category!r}")
    by_period = {row.period: row for row in selected}
    output: list[dict[str, object]] = []

    for row in sorted(selected, key=lambda item: item.period):
        comparison_period = _shift_period(row.period, offset)
        previous = by_period.get(comparison_period)
        status = "computed"
        null_reason = ""
        growth: float | None = None

        if row.actual_spend is None:
            status = "current_actual_spend_null"
            null_reason = row.notes
            previous_value = (
                "unavailable"
                if previous is None
                else "NULL" if previous.actual_spend is None else str(previous.actual_spend)
            )
            formula = f"Cannot compute: ((NULL - {previous_value}) / {previous_value}) * 100"
        elif previous is None:
            status = "comparison_period_unavailable"
            formula = f"Cannot compute: comparison value for {comparison_period} is unavailable"
        elif previous.actual_spend is None:
            status = "comparison_actual_spend_null"
            null_reason = previous.notes
            formula = f"Cannot compute: (({row.actual_spend} - NULL) / NULL) * 100"
        elif previous.actual_spend == 0:
            raise RefusalError(
                f"cannot compute {growth_label} for {row.period}: "
                f"{comparison_period} actual_spend is zero"
            )
        else:
            growth = ((row.actual_spend - previous.actual_spend) / previous.actual_spend) * 100
            formula = (
                f"(({row.actual_spend} - {previous.actual_spend}) / "
                f"{previous.actual_spend}) * 100 = {growth:.1f}%"
            )

        output.append(
            {
                "period": row.period,
                "ward": row.ward,
                "category": row.category,
                "actual_spend": "" if row.actual_spend is None else row.actual_spend,
                "growth_type": growth_label,
                "comparison_period": comparison_period,
                "comparison_actual_spend": (
                    "" if previous is None or previous.actual_spend is None else previous.actual_spend
                ),
                "growth_percent": "" if growth is None else f"{growth:.1f}",
                "formula": formula,
                "status": status,
                "null_reason": null_reason,
            }
        )
    return output


def _report_nulls(null_rows: list[BudgetRow]) -> None:
    print(f"Null actual_spend audit: {len(null_rows)} row(s)", file=sys.stderr)
    for row in null_rows:
        print(
            f"- {row.period} | {row.ward} | {row.category} | reason: {row.notes}",
            file=sys.stderr,
        )


def _write_output(path: str | Path, rows: list[dict[str, object]]) -> None:
    destination = Path(path)
    try:
        with destination.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        raise RefusalError(f"cannot write output CSV {destination}: {exc}") from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute actual-spend growth for one ward and one category."
    )
    parser.add_argument("--input", required=True, help="Path to the source budget CSV")
    parser.add_argument("--ward", help="Exact ward name (all-ward aggregation is refused)")
    parser.add_argument("--category", help="Exact category name (aggregation is refused)")
    parser.add_argument("--growth-type", help="Required growth formula: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path for the output CSV")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        rows, null_rows = load_dataset(args.input)
        _report_nulls(null_rows)
        growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
        _write_output(args.output, growth_rows)
    except RefusalError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {len(growth_rows)} per-period rows to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
