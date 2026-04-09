"""UC-0C growth calculator with strict operational guardrails."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

MISSING_GROWTH_TYPE_REFUSAL = (
    "Refused: --growth-type is required. Please specify a growth type "
    "(e.g., MoM or YoY)."
)

UNSAFE_AGGREGATION_REFUSAL = (
    "Refused: Aggregating across wards/categories is disabled by UC-0C "
    "guardrails unless you explicitly authorize that aggregation scope."
)

MOM_FORMULA = "((current_actual_spend - previous_actual_spend) / previous_actual_spend) * 100"
YOY_FORMULA = "((current_actual_spend - same_month_last_year_actual_spend) / same_month_last_year_actual_spend) * 100"


@dataclass
class DatasetLoadResult:
    rows: List[Dict[str, object]]
    row_count: int
    column_count: int
    null_count: int
    null_rows: List[Dict[str, str]]


def parse_period(period_value: str) -> datetime:
    return datetime.strptime(period_value, "%Y-%m")


def normalize_actual_spend(value: str) -> Optional[float]:
    if value is None:
        return None
    raw_value = str(value).strip()
    if raw_value == "":
        return None
    return float(raw_value)


def load_dataset(input_path: str) -> DatasetLoadResult:
    csv_path = Path(input_path)
    if not csv_path.exists() or not csv_path.is_file():
        raise ValueError(f"Input file not found: {input_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file_handle:
        reader = csv.DictReader(file_handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is missing headers")

        missing_columns = REQUIRED_COLUMNS.difference(set(reader.fieldnames))
        if missing_columns:
            missing_list = ", ".join(sorted(missing_columns))
            raise ValueError(f"Missing required columns: {missing_list}")

        parsed_rows: List[Dict[str, object]] = []
        null_rows: List[Dict[str, str]] = []
        for raw_row in reader:
            period = str(raw_row["period"]).strip()
            try:
                parsed_period = parse_period(period)
            except ValueError as period_error:
                raise ValueError(f"Invalid period format '{period}'. Expected YYYY-MM") from period_error

            actual_spend = normalize_actual_spend(raw_row["actual_spend"])
            normalized_row: Dict[str, object] = {
                "period": period,
                "period_dt": parsed_period,
                "ward": str(raw_row["ward"]).strip(),
                "category": str(raw_row["category"]).strip(),
                "budgeted_amount": float(str(raw_row["budgeted_amount"]).strip()),
                "actual_spend": actual_spend,
                "notes": str(raw_row.get("notes", "")).strip(),
            }

            parsed_rows.append(normalized_row)

            if actual_spend is None:
                null_rows.append(
                    {
                        "period": normalized_row["period"],
                        "ward": normalized_row["ward"],
                        "category": normalized_row["category"],
                        "notes": normalized_row["notes"],
                    }
                )

    return DatasetLoadResult(
        rows=parsed_rows,
        row_count=len(parsed_rows),
        column_count=len(REQUIRED_COLUMNS),
        null_count=len(null_rows),
        null_rows=null_rows,
    )


def month_key(period_dt: datetime) -> Tuple[int, int]:
    return period_dt.year, period_dt.month


def find_comparison_row(
    row: Dict[str, object],
    row_by_month: Dict[Tuple[int, int], Dict[str, object]],
    growth_type: str,
) -> Tuple[Optional[Dict[str, object]], str]:
    period_dt: datetime = row["period_dt"]  # type: ignore[assignment]
    if growth_type == "MOM":
        if period_dt.month == 1:
            return None, "No previous month available for MoM comparison"
        previous_year = period_dt.year
        previous_month = period_dt.month - 1
        comparison_key = (previous_year, previous_month)
        comparison_row = row_by_month.get(comparison_key)
        if comparison_row is None:
            return None, "Previous month row is missing for MoM comparison"
        return comparison_row, ""

    previous_year_key = (period_dt.year - 1, period_dt.month)
    comparison_row = row_by_month.get(previous_year_key)
    if comparison_row is None:
        return None, "Same month previous year row is missing for YoY comparison"
    return comparison_row, ""


def compute_growth(
    rows: List[Dict[str, object]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, object]]:
    growth_type_normalized = growth_type.upper()
    if growth_type_normalized not in {"MOM", "YOY"}:
        raise ValueError("Unsupported growth type. Allowed values: MoM, YoY")

    scoped_rows = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    scoped_rows.sort(key=lambda item: item["period_dt"])

    row_by_month = {month_key(row["period_dt"]): row for row in scoped_rows}
    formula = MOM_FORMULA if growth_type_normalized == "MOM" else YOY_FORMULA

    output_rows: List[Dict[str, object]] = []
    for row in scoped_rows:
        current_actual = row["actual_spend"]
        if current_actual is None:
            output_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": "",
                    "growth_type": growth_type_normalized,
                    "formula": formula,
                    "growth_percent": "",
                    "status": "flagged_null",
                    "reason": row["notes"] or "actual_spend is null",
                }
            )
            continue

        comparison_row, comparison_reason = find_comparison_row(
            row,
            row_by_month,
            growth_type_normalized,
        )
        if comparison_row is None:
            output_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": f"{current_actual:.1f}",
                    "growth_type": growth_type_normalized,
                    "formula": formula,
                    "growth_percent": "",
                    "status": "not_computed",
                    "reason": comparison_reason,
                }
            )
            continue

        comparison_actual = comparison_row["actual_spend"]
        if comparison_actual is None:
            output_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": f"{current_actual:.1f}",
                    "growth_type": growth_type_normalized,
                    "formula": formula,
                    "growth_percent": "",
                    "status": "not_computed",
                    "reason": "Comparison period actual_spend is null",
                }
            )
            continue

        if comparison_actual == 0:
            output_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": f"{current_actual:.1f}",
                    "growth_type": growth_type_normalized,
                    "formula": formula,
                    "growth_percent": "",
                    "status": "not_computed",
                    "reason": "Comparison period actual_spend is zero; division by zero",
                }
            )
            continue

        growth_percent = ((current_actual - comparison_actual) / comparison_actual) * 100
        output_rows.append(
            {
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": f"{current_actual:.1f}",
                "growth_type": growth_type_normalized,
                "formula": formula,
                "growth_percent": f"{growth_percent:.1f}",
                "status": "computed",
                "reason": "",
            }
        )

    return output_rows


def write_output(output_path: str, rows: List[Dict[str, object]]) -> None:
    output_columns = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_percent",
        "status",
        "reason",
    ]
    output_file = Path(output_path)
    with output_file.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(rows)


def print_null_report(null_rows: List[Dict[str, str]]) -> None:
    print(f"Detected {len(null_rows)} null actual_spend rows before computation:")
    for null_row in null_rows:
        print(
            f"- period={null_row['period']} | ward={null_row['ward']} | "
            f"category={null_row['category']} | notes={null_row['notes']}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UC-0C guarded growth calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", help="Ward name for scoped calculation")
    parser.add_argument("--category", help="Category for scoped calculation")
    parser.add_argument("--growth-type", help="Growth type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument(
        "--allow-aggregation",
        action="store_true",
        help="Explicit authorization to compute across wards/categories",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.growth_type:
        print(MISSING_GROWTH_TYPE_REFUSAL)
        raise SystemExit(1)

    if (not args.ward or not args.category) and not args.allow_aggregation:
        print(UNSAFE_AGGREGATION_REFUSAL)
        raise SystemExit(1)

    dataset = load_dataset(args.input)
    print_null_report(dataset.null_rows)

    rows_to_write: List[Dict[str, object]] = []

    if args.ward and args.category:
        rows_to_write = compute_growth(
            rows=dataset.rows,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
    else:
        ward_category_pairs = sorted(
            {(row["ward"], row["category"]) for row in dataset.rows},
            key=lambda pair: (pair[0], pair[1]),
        )
        for ward, category in ward_category_pairs:
            rows_to_write.extend(
                compute_growth(
                    rows=dataset.rows,
                    ward=ward,
                    category=category,
                    growth_type=args.growth_type,
                )
            )

    write_output(args.output, rows_to_write)
    print(f"Wrote {len(rows_to_write)} rows to {args.output}")


if __name__ == "__main__":
    main()
