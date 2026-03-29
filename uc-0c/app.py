"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


class ValidationError(Exception):
    """Raised when dataset or request validation fails."""


@dataclass
class BudgetRow:
    period: str
    ward: str
    category: str
    budgeted_amount: float
    actual_spend: Optional[float]
    notes: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compute per-period growth for a single ward/category using explicit growth"
            " type and null-safe handling."
        )
    )
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth type: MoM or YoY",
    )
    parser.add_argument("--output", required=True, help="Path to output CSV")
    return parser.parse_args()


def _parse_float(raw: str, field_name: str) -> Optional[float]:
    value = (raw or "").strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise ValidationError(f"Invalid numeric value in {field_name}: '{raw}'") from exc


def _validate_period(period: str) -> None:
    # Scope is fixed to Jan-Dec 2024 for this UC.
    if not re.fullmatch(r"2024-(0[1-9]|1[0-2])", period):
        raise ValidationError(
            f"Out-of-scope period '{period}'. Expected YYYY-MM within 2024-01..2024-12."
        )


def load_dataset(input_path: Path) -> List[BudgetRow]:
    if not input_path.exists():
        raise ValidationError(f"Input file not found: {input_path}")

    rows: List[BudgetRow] = []
    with input_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValidationError("Input CSV has no header row.")

        header = {h.strip() for h in reader.fieldnames if h is not None}
        missing = REQUIRED_COLUMNS - header
        if missing:
            raise ValidationError(
                f"Input CSV missing required columns: {', '.join(sorted(missing))}"
            )

        for idx, row in enumerate(reader, start=2):
            period = (row.get("period") or "").strip()
            ward = (row.get("ward") or "").strip()
            category = (row.get("category") or "").strip()
            notes = (row.get("notes") or "").strip()

            if not period or not ward or not category:
                raise ValidationError(f"Row {idx}: period/ward/category cannot be empty.")

            _validate_period(period)

            budgeted_amount = _parse_float(row.get("budgeted_amount", ""), "budgeted_amount")
            actual_spend = _parse_float(row.get("actual_spend", ""), "actual_spend")

            if budgeted_amount is None:
                raise ValidationError(f"Row {idx}: budgeted_amount cannot be null/blank.")

            rows.append(
                BudgetRow(
                    period=period,
                    ward=ward,
                    category=category,
                    budgeted_amount=budgeted_amount,
                    actual_spend=actual_spend,
                    notes=notes,
                )
            )

    return rows


def validate_request(ward: str, category: str, growth_type: str) -> str:
    if not ward.strip() or not category.strip():
        raise ValidationError("Both --ward and --category are required.")

    lowered_ward = ward.strip().lower()
    lowered_category = category.strip().lower()
    disallowed = {"any", "all", "*", "all wards", "all categories"}
    if lowered_ward in disallowed or lowered_category in disallowed:
        raise ValidationError(
            "Refused: cross-ward or cross-category aggregation is not allowed without explicit override."
        )

    gt = growth_type.strip().lower()
    if gt not in {"mom", "yoy"}:
        raise ValidationError(
            "Refused: --growth-type missing or ambiguous. Provide explicit growth type: MoM or YoY."
        )
    return gt.upper()


def find_null_rows(rows: Sequence[BudgetRow]) -> List[BudgetRow]:
    return [r for r in rows if r.actual_spend is None]


def report_null_rows(null_rows: Sequence[BudgetRow]) -> None:
    print(f"NULL_ROWS_FOUND={len(null_rows)}")
    for r in sorted(null_rows, key=lambda x: (x.period, x.ward, x.category)):
        reason = r.notes if r.notes else "No reason provided"
        print(f"NULL_ROW period={r.period} ward={r.ward} category={r.category} reason={reason}")


def compute_growth(
    rows: Sequence[BudgetRow],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    scoped = [r for r in rows if r.ward == ward and r.category == category]
    if not scoped:
        raise ValidationError(
            f"No rows found for ward='{ward}' and category='{category}'."
        )

    scoped = sorted(scoped, key=lambda r: r.period)
    period_index = {r.period: r for r in scoped}

    out: List[Dict[str, str]] = []
    for i, row in enumerate(scoped):
        current = row.actual_spend
        formula_used = ""
        growth_value: Optional[float] = None
        status = "computed"

        if current is None:
            status = "null_actual_spend"
            formula_used = "not_computed: actual_spend is null"
        elif growth_type == "MOM":
            formula_used = "MoM: (current - previous) / previous"
            if i == 0:
                status = "not_computed_no_previous"
            else:
                prev = scoped[i - 1].actual_spend
                if prev is None:
                    status = "not_computed_previous_null"
                elif prev == 0:
                    status = "not_computed_previous_zero"
                else:
                    growth_value = (current - prev) / prev
        else:  # YOY
            formula_used = "YoY: (current - same_month_last_year) / same_month_last_year"
            year, month = row.period.split("-")
            prev_year_period = f"{int(year) - 1:04d}-{month}"
            prev_row = period_index.get(prev_year_period)
            if prev_row is None:
                status = "not_computed_no_prior_year"
            elif prev_row.actual_spend is None:
                status = "not_computed_prior_year_null"
            elif prev_row.actual_spend == 0:
                status = "not_computed_prior_year_zero"
            else:
                growth_value = (current - prev_row.actual_spend) / prev_row.actual_spend

        out.append(
            {
                "period": row.period,
                "ward": row.ward,
                "category": row.category,
                "actual_spend": "" if current is None else f"{current:.6f}",
                "growth_type": growth_type,
                "growth_value": "" if growth_value is None else f"{growth_value:.6f}",
                "formula_used": formula_used,
                "status": status,
                "notes": row.notes,
            }
        )

    return out


def write_output(output_path: Path, output_rows: Sequence[Dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_value",
        "formula_used",
        "status",
        "notes",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

def main():
    args = parse_args()
    try:
        growth_type = validate_request(args.ward, args.category, args.growth_type)
        rows = load_dataset(Path(args.input))

        # Enforcement: null rows must be reported before any growth computation.
        null_rows = find_null_rows(rows)
        report_null_rows(null_rows)

        output_rows = compute_growth(rows, args.ward, args.category, growth_type)
        write_output(Path(args.output), output_rows)
        print(f"WROTE_OUTPUT={args.output}")
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
