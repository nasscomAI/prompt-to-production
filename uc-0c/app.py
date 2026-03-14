"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

SUPPORTED_GROWTH_TYPES = {"mom", "yoy"}


@dataclass
class BudgetRow:
    period: str
    ward: str
    category: str
    budgeted_amount: float
    actual_spend: Optional[float]
    notes: str


def _parse_period(period: str) -> datetime:
    try:
        return datetime.strptime(period, "%Y-%m")
    except ValueError as exc:
        raise ValueError(f"Invalid period format: {period}. Expected YYYY-MM.") from exc


def _parse_float(value: str, field_name: str, row_idx: int) -> Optional[float]:
    value = (value or "").strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name} at row {row_idx}: {value}") from exc


def load_dataset(input_path: str) -> Tuple[List[BudgetRow], List[Dict[str, str]]]:
    """Read CSV, validate required schema and return parsed rows with null-row audit."""
    try:
        with open(input_path, "r", encoding="utf-8", newline="") as infile:
            reader = csv.DictReader(infile)
            headers = set(reader.fieldnames or [])
            missing = REQUIRED_COLUMNS - headers
            if missing:
                missing_cols = ", ".join(sorted(missing))
                raise ValueError(f"Missing required columns: {missing_cols}")

            parsed_rows: List[BudgetRow] = []
            null_rows: List[Dict[str, str]] = []

            for idx, row in enumerate(reader, start=2):
                period = (row.get("period") or "").strip()
                ward = (row.get("ward") or "").strip()
                category = (row.get("category") or "").strip()
                notes = (row.get("notes") or "").strip()

                _parse_period(period)
                budgeted_amount = _parse_float(row.get("budgeted_amount", ""), "budgeted_amount", idx)
                if budgeted_amount is None:
                    raise ValueError(f"budgeted_amount cannot be null at row {idx}")

                actual_spend = _parse_float(row.get("actual_spend", ""), "actual_spend", idx)

                parsed = BudgetRow(
                    period=period,
                    ward=ward,
                    category=category,
                    budgeted_amount=budgeted_amount,
                    actual_spend=actual_spend,
                    notes=notes,
                )
                parsed_rows.append(parsed)

                if actual_spend is None:
                    null_rows.append(
                        {
                            "period": period,
                            "ward": ward,
                            "category": category,
                            "notes": notes or "No reason provided",
                        }
                    )

    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input dataset not found: {input_path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to read dataset: {input_path}") from exc

    return parsed_rows, null_rows


def _prev_period(period: str, growth_type: str) -> str:
    dt = _parse_period(period)
    if growth_type == "mom":
        year = dt.year
        month = dt.month - 1
        if month == 0:
            month = 12
            year -= 1
        return f"{year:04d}-{month:02d}"
    return f"{dt.year - 1:04d}-{dt.month:02d}"


def _validate_scope(ward: str, category: str) -> None:
    ward_lc = ward.strip().lower()
    category_lc = category.strip().lower()
    blocked_tokens = {"all", "*", "any"}
    if ward_lc in blocked_tokens or category_lc in blocked_tokens:
        raise ValueError("Refused: aggregation across wards/categories is not allowed for this task.")


def _build_not_computed_row(
    row: BudgetRow,
    growth_key: str,
    compare_period: str,
    compare_val: Optional[float],
    formula_base: str,
    flag: str,
    reason: str,
) -> Dict[str, str]:
    return {
        "period": row.period,
        "ward": row.ward,
        "category": row.category,
        "growth_type": growth_key.upper(),
        "actual_spend": "NULL" if row.actual_spend is None else f"{row.actual_spend:.1f}",
        "comparison_period": compare_period,
        "comparison_actual_spend": "NULL" if compare_val is None else f"{compare_val:.1f}",
        "formula": formula_base,
        "growth_percent": "",
        "status": "NOT_COMPUTED",
        "flag": flag,
        "reason": reason,
        "notes": row.notes,
    }


def _compute_row_growth(
    row: BudgetRow,
    compare_row: Optional[BudgetRow],
    compare_period: str,
    growth_key: str,
) -> Dict[str, str]:
    current_val = row.actual_spend
    compare_val = compare_row.actual_spend if compare_row else None
    formula_base = "((current_actual_spend - comparison_actual_spend) / comparison_actual_spend) * 100"

    if compare_row is None:
        formula = f"{formula_base} | values: current={current_val if current_val is not None else 'NULL'}, comparison=NULL"
        return _build_not_computed_row(
            row,
            growth_key,
            compare_period,
            compare_val,
            formula,
            "NO_COMPARISON_PERIOD",
            f"Comparison period {compare_period} is not available in scoped data.",
        )

    if current_val is None:
        formula = f"{formula_base} | values: current=NULL, comparison={compare_val}"
        return _build_not_computed_row(
            row,
            growth_key,
            compare_period,
            compare_val,
            formula,
            "NULL_CURRENT",
            f"Current actual_spend is NULL. Reason: {row.notes or 'No reason provided'}",
        )

    if compare_val is None:
        formula = f"{formula_base} | values: current={current_val}, comparison=NULL"
        return _build_not_computed_row(
            row,
            growth_key,
            compare_period,
            compare_val,
            formula,
            "NULL_COMPARISON",
            f"Comparison actual_spend is NULL for {compare_period}. Reason: {compare_row.notes or 'No reason provided'}",
        )

    if compare_val == 0:
        formula = f"{formula_base} | values: current={current_val}, comparison=0"
        return _build_not_computed_row(
            row,
            growth_key,
            compare_period,
            compare_val,
            formula,
            "ZERO_DENOMINATOR",
            "Comparison actual_spend is zero; growth formula denominator cannot be zero.",
        )

    growth = ((current_val - compare_val) / compare_val) * 100
    return {
        "period": row.period,
        "ward": row.ward,
        "category": row.category,
        "growth_type": growth_key.upper(),
        "actual_spend": f"{current_val:.1f}",
        "comparison_period": compare_period,
        "comparison_actual_spend": f"{compare_val:.1f}",
        "formula": f"(({current_val:.1f} - {compare_val:.1f}) / {compare_val:.1f}) * 100",
        "growth_percent": f"{growth:.1f}%",
        "status": "COMPUTED",
        "flag": "",
        "reason": "",
        "notes": row.notes,
    }


def compute_growth(rows: List[BudgetRow], ward: str, category: str, growth_type: str) -> List[Dict[str, str]]:
    """Compute per-period growth for a specific ward+category with explicit formulas."""
    if not growth_type:
        raise ValueError("Missing --growth-type. Provide one of: MoM, YoY")

    growth_key = growth_type.strip().lower()
    if growth_key not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(f"Unsupported growth type: {growth_type}. Use MoM or YoY.")

    _validate_scope(ward, category)

    scoped = [
        row for row in rows
        if row.ward == ward and row.category == category
    ]

    if not scoped:
        raise ValueError("No rows found for the provided ward and category.")

    scoped_sorted = sorted(scoped, key=lambda r: _parse_period(r.period))
    period_map: Dict[str, BudgetRow] = {row.period: row for row in scoped_sorted}
    output_rows: List[Dict[str, str]] = []

    for row in scoped_sorted:
        compare_period = _prev_period(row.period, growth_key)
        compare_row = period_map.get(compare_period)
        output_rows.append(_compute_row_growth(row, compare_row, compare_period, growth_key))

    return output_rows


def _write_output(output_path: str, rows: List[Dict[str, str]]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "growth_type",
        "actual_spend",
        "comparison_period",
        "comparison_actual_spend",
        "formula",
        "growth_percent",
        "status",
        "flag",
        "reason",
        "notes",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _print_null_audit(null_rows: List[Dict[str, str]]) -> None:
    print(f"Null audit: {len(null_rows)} rows with NULL actual_spend found.")
    for row in null_rows:
        print(
            " - "
            f"{row['period']} | {row['ward']} | {row['category']} | reason: {row['notes']}"
        )


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward value")
    parser.add_argument("--category", required=True, help="Exact category value")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    _print_null_audit(null_rows)
    growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    _write_output(args.output, growth_rows)

    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()
