"""UC-0C — scoped, null-aware municipal budget growth analysis."""

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Union


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}
FORMULAS = {
    "MoM": "((current actual_spend - previous month actual_spend) / previous month actual_spend) * 100",
    "YoY": "((current actual_spend - same month last year actual_spend) / same month last year actual_spend) * 100",
}
OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "actual_spend",
    "comparison_period",
    "comparison_actual_spend",
    "growth_type",
    "formula",
    "growth_percent",
    "status",
    "notes",
]


@dataclass(frozen=True)
class BudgetRow:
    period: str
    period_date: datetime
    ward: str
    category: str
    budgeted_amount: float
    actual_spend: Optional[float]
    notes: str


def _parse_number(value: str, field: str, row_number: int) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Row {row_number}: {field} must be a number, got {value!r}"
        ) from exc


def load_dataset(input_path: Union[str, Path]) -> list[BudgetRow]:
    """Load CSV data, validate its structure, and disclose all null spends."""
    path = Path(input_path)
    if path.suffix.lower() != ".csv":
        raise ValueError("Input must be a .csv file")

    rows: list[BudgetRow] = []
    seen_keys: set[tuple[str, str, str]] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        missing_columns = sorted(REQUIRED_COLUMNS - columns)
        if missing_columns:
            raise ValueError(
                "Input is missing required columns: " + ", ".join(missing_columns)
            )

        for row_number, raw in enumerate(reader, start=2):
            period = (raw["period"] or "").strip()
            ward = (raw["ward"] or "").strip()
            category = (raw["category"] or "").strip()
            notes = (raw["notes"] or "").strip()
            if not period or not ward or not category:
                raise ValueError(
                    f"Row {row_number}: period, ward and category are required"
                )
            try:
                period_date = datetime.strptime(period, "%Y-%m")
            except ValueError as exc:
                raise ValueError(
                    f"Row {row_number}: period must use YYYY-MM, got {period!r}"
                ) from exc

            key = (period, ward, category)
            if key in seen_keys:
                raise ValueError(
                    f"Row {row_number}: duplicate period/ward/category: {key}"
                )
            seen_keys.add(key)

            actual_text = (raw["actual_spend"] or "").strip()
            actual_spend = (
                None
                if not actual_text
                else _parse_number(actual_text, "actual_spend", row_number)
            )
            if actual_spend is None and not notes:
                raise ValueError(
                    f"Row {row_number}: null actual_spend requires a reason in notes"
                )

            rows.append(
                BudgetRow(
                    period=period,
                    period_date=period_date,
                    ward=ward,
                    category=category,
                    budgeted_amount=_parse_number(
                        (raw["budgeted_amount"] or "").strip(),
                        "budgeted_amount",
                        row_number,
                    ),
                    actual_spend=actual_spend,
                    notes=notes,
                )
            )

    if not rows:
        raise ValueError("Input dataset contains no data rows")

    null_rows = [row for row in rows if row.actual_spend is None]
    print(f"Null actual_spend rows: {len(null_rows)}")
    for row in null_rows:
        print(
            f"  {row.period} | {row.ward} | {row.category} | "
            f"reason: {row.notes}"
        )
    return rows


def _comparison_period(period: datetime, growth_type: str) -> str:
    if growth_type == "MoM":
        year = period.year if period.month > 1 else period.year - 1
        month = period.month - 1 if period.month > 1 else 12
    else:
        year = period.year - 1
        month = period.month
    return f"{year:04d}-{month:02d}"


def _reject_aggregate_scope(label: str, value: str) -> None:
    normalised = value.strip().casefold()
    if normalised in {"all", "any", "*", "all wards", "all categories"} or "," in value:
        raise ValueError(
            f"Refusing cross-{label} aggregation. Specify exactly one {label}."
        )


def compute_growth(
    rows: list[BudgetRow], ward: str, category: str, growth_type: str
) -> list[dict[str, str]]:
    """Return transparent per-period growth for one ward/category selection."""
    if growth_type not in FORMULAS:
        raise ValueError("growth_type is required and must be exactly MoM or YoY")
    _reject_aggregate_scope("ward", ward)
    _reject_aggregate_scope("category", category)

    wards = {row.ward for row in rows}
    categories = {row.category for row in rows}
    if ward not in wards:
        raise ValueError(f"Unknown ward: {ward!r}")
    if category not in categories:
        raise ValueError(f"Unknown category: {category!r}")

    selected = sorted(
        (row for row in rows if row.ward == ward and row.category == category),
        key=lambda row: row.period_date,
    )
    if not selected:
        raise ValueError(f"No rows found for ward {ward!r} and category {category!r}")

    by_period = {row.period: row for row in selected}
    output: list[dict[str, str]] = []
    for current in selected:
        comparison_period = _comparison_period(current.period_date, growth_type)
        comparison = by_period.get(comparison_period)
        growth = ""
        notes = current.notes

        if current.actual_spend is None:
            status = "not_computed_current_null"
            notes = f"Current actual_spend is null: {current.notes}"
        elif comparison is None:
            status = "not_computed_history_unavailable"
            notes = f"No {comparison_period} row is available for comparison"
        elif comparison.actual_spend is None:
            status = "not_computed_comparison_null"
            notes = (
                f"Comparison actual_spend is null at {comparison_period}: "
                f"{comparison.notes}"
            )
        elif comparison.actual_spend == 0:
            status = "not_computed_zero_denominator"
            notes = f"Comparison actual_spend is zero at {comparison_period}"
        else:
            growth_value = (
                (current.actual_spend - comparison.actual_spend)
                / comparison.actual_spend
                * 100
            )
            growth = f"{growth_value:.1f}"
            status = "computed"

        output.append(
            {
                "period": current.period,
                "ward": current.ward,
                "category": current.category,
                "actual_spend": (
                    "" if current.actual_spend is None else f"{current.actual_spend:.1f}"
                ),
                "comparison_period": comparison_period,
                "comparison_actual_spend": (
                    ""
                    if comparison is None or comparison.actual_spend is None
                    else f"{comparison.actual_spend:.1f}"
                ),
                "growth_type": growth_type,
                "formula": FORMULAS[growth_type],
                "growth_percent": growth,
                "status": status,
                "notes": notes,
            }
        )
    return output


def write_output(
    output_rows: list[dict[str, str]], output_path: Union[str, Path]
) -> None:
    path = Path(output_path)
    with path.open("w", encoding="utf-8-sig", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute scoped, null-aware municipal budget growth"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="One exact ward name")
    parser.add_argument("--category", required=True, help="One exact category name")
    parser.add_argument(
        "--growth-type",
        help="Required growth formula: MoM or YoY (the program will not guess)",
    )
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    if args.growth_type is None:
        parser.error("--growth-type is required; specify MoM or YoY. I will not guess.")

    try:
        rows = load_dataset(args.input)
        output_rows = compute_growth(
            rows, args.ward, args.category, args.growth_type
        )
        write_output(output_rows, args.output)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print(
        f"Done. Wrote {len(output_rows)} per-period rows for exactly one ward "
        f"and category to {args.output}"
    )


if __name__ == "__main__":
    main()
