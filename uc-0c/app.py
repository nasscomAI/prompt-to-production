"""
UC-0C - Number That Looks Right
Per-ward, per-category growth computation with strict null/formula handling.
"""
import argparse
import csv
import re
from typing import Dict, List, Tuple


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def _norm(value: str) -> str:
    return (value or "").strip().lower()


def _parse_float(value: str) -> float:
    return float(str(value).strip())


def _validate_period(value: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{2}$", (value or "").strip()))


def load_dataset(input_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Read CSV, validate schema/rows, and return (rows, null_rows_report).
    """
    try:
        with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV has no header row.")
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing_cols:
                raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
            rows = list(reader)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input file not found: {input_path}") from exc

    validation_errors: List[str] = []
    null_rows: List[Dict[str, str]] = []
    for idx, row in enumerate(rows, start=2):
        period = (row.get("period") or "").strip()
        if not _validate_period(period):
            validation_errors.append(f"Row {idx}: invalid period '{period}', expected YYYY-MM.")

        budgeted_amount = (row.get("budgeted_amount") or "").strip()
        try:
            _parse_float(budgeted_amount)
        except Exception:
            validation_errors.append(f"Row {idx}: invalid budgeted_amount '{budgeted_amount}'.")

        actual_spend = (row.get("actual_spend") or "").strip()
        if actual_spend == "":
            null_rows.append(
                {
                    "period": period,
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": row.get("notes", ""),
                }
            )
        else:
            try:
                _parse_float(actual_spend)
            except Exception:
                validation_errors.append(f"Row {idx}: invalid actual_spend '{actual_spend}'.")

    if validation_errors:
        raise ValueError("Dataset validation failed:\n" + "\n".join(validation_errors))

    return rows, null_rows


def _refuse_aggregate_like_input(ward: str, category: str) -> None:
    aggregate_tokens = {"all", "any", "*", "overall", "total", "combined"}
    if _norm(ward) in aggregate_tokens or _norm(category) in aggregate_tokens:
        raise ValueError(
            "Refused: aggregation across wards/categories is not allowed without explicit authorization."
        )


def _period_to_sort_key(period: str) -> Tuple[int, int]:
    year, month = period.split("-")
    return int(year), int(month)


def _format_growth(value: float) -> str:
    if value >= 0:
        return f"+{value:.1f}%"
    return f"{value:.1f}%"


def compute_growth(
    rows: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    """
    Compute per-period growth table for exactly one ward-category slice.
    """
    if not growth_type:
        raise ValueError("Refused: --growth-type is required (use MoM or YoY).")

    growth_type_norm = _norm(growth_type)
    if growth_type_norm not in {"mom", "yoy"}:
        raise ValueError(f"Unsupported growth type '{growth_type}'. Use MoM or YoY.")

    _refuse_aggregate_like_input(ward, category)

    filtered = [
        row
        for row in rows
        if (row.get("ward") or "").strip() == ward and (row.get("category") or "").strip() == category
    ]
    if not filtered:
        raise ValueError(f"No rows found for ward='{ward}' and category='{category}'.")

    filtered.sort(key=lambda r: _period_to_sort_key((r.get("period") or "").strip()))
    period_map = {(row.get("period") or "").strip(): row for row in filtered}

    out: List[Dict[str, str]] = []
    for idx, row in enumerate(filtered):
        period = (row.get("period") or "").strip()
        budgeted_raw = (row.get("budgeted_amount") or "").strip()
        actual_raw = (row.get("actual_spend") or "").strip()
        notes = (row.get("notes") or "").strip()

        budgeted = _parse_float(budgeted_raw)
        formula_used = (
            "((current_actual_spend - previous_actual_spend) / previous_actual_spend) * 100"
            if growth_type_norm == "mom"
            else "((current_actual_spend - prior_year_same_month_actual_spend) / prior_year_same_month_actual_spend) * 100"
        )

        status = "OK"
        reason = ""
        growth_value = ""

        if actual_raw == "":
            status = "NOT_COMPUTED"
            reason = f"Current period actual_spend is NULL. Notes: {notes or 'No note provided.'}"
        else:
            current_actual = _parse_float(actual_raw)
            prev_row = None
            if growth_type_norm == "mom":
                if idx == 0:
                    status = "NOT_COMPUTED"
                    reason = "No previous month available for MoM baseline."
                else:
                    prev_row = filtered[idx - 1]
            else:
                y, m = _period_to_sort_key(period)
                prev_period = f"{y - 1:04d}-{m:02d}"
                prev_row = period_map.get(prev_period)
                if prev_row is None:
                    status = "NOT_COMPUTED"
                    reason = f"No prior-year baseline row for YoY ({prev_period})."

            if prev_row is not None and status == "OK":
                prev_actual_raw = (prev_row.get("actual_spend") or "").strip()
                prev_period = (prev_row.get("period") or "").strip()
                if prev_actual_raw == "":
                    status = "NOT_COMPUTED"
                    prev_notes = (prev_row.get("notes") or "").strip()
                    reason = (
                        f"Baseline period {prev_period} actual_spend is NULL. "
                        f"Notes: {prev_notes or 'No note provided.'}"
                    )
                else:
                    prev_actual = _parse_float(prev_actual_raw)
                    if prev_actual == 0:
                        status = "NOT_COMPUTED"
                        reason = f"Baseline period {prev_period} actual_spend is 0; division undefined."
                    else:
                        growth_pct = ((current_actual - prev_actual) / prev_actual) * 100.0
                        growth_value = _format_growth(growth_pct)

        out.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": f"{budgeted:.1f}",
                "actual_spend": actual_raw if actual_raw != "" else "NULL",
                "growth_type": growth_type_norm.upper(),
                "formula_used": formula_used,
                "growth_result": growth_value,
                "status": status,
                "reason": reason,
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C Ward Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward budget CSV")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument(
        "--growth-type",
        dest="growth_type",
        required=False,
        help="Growth type: MoM or YoY",
    )
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    if not args.growth_type:
        raise ValueError("Refused: --growth-type not specified. Please provide MoM or YoY.")

    rows, null_rows = load_dataset(args.input)

    print(f"Detected {len(null_rows)} null actual_spend rows before computation:")
    for row in null_rows:
        print(
            f"- {row['period']} | {row['ward']} | {row['category']} | notes: {row['notes'] or 'No note provided.'}"
        )

    growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=[
                "period",
                "ward",
                "category",
                "budgeted_amount",
                "actual_spend",
                "growth_type",
                "formula_used",
                "growth_result",
                "status",
                "reason",
            ],
        )
        writer.writeheader()
        writer.writerows(growth_rows)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
