"""UC-0C budget growth calculator."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]
PERIOD_PATTERN = re.compile(r"^\d{4}-\d{2}$")
VALID_GROWTH_TYPES = {"MOM", "YOY"}


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
        description="Compute budget growth per period for one ward and category."
    )
    parser.add_argument("--input", required=True, help="Path to input CSV.")
    parser.add_argument("--ward", required=True, help="Ward name (single ward only).")
    parser.add_argument(
        "--category", required=True, help="Category name (single category only)."
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth type: MoM or YoY.",
    )
    parser.add_argument("--output", required=True, help="Path to output CSV.")
    return parser.parse_args()


def fail(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def safe_float(value: str, column_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        fail(f"Invalid numeric value in `{column_name}`: {value!r}")


def normalize_growth_type(growth_type: str) -> str:
    if not growth_type or not growth_type.strip():
        fail("`--growth-type` is required. Refusing to guess; choose MoM or YoY.")
    normalized = growth_type.strip().upper()
    if normalized not in VALID_GROWTH_TYPES:
        fail(
            f"Unsupported growth type {growth_type!r}. "
            "Refusing to guess; choose one of: MoM, YoY."
        )
    return normalized


def ensure_not_aggregate_request(value: str, field_name: str) -> None:
    lowered = value.strip().lower()
    forbidden = {"all", "any", "*", "overall", "all wards", "all categories"}
    if lowered in forbidden:
        fail(
            f"Refusing {field_name}={value!r}. "
            "This tool only supports a single ward and single category."
        )


def load_dataset(csv_path: Path) -> Dict[str, object]:
    if not csv_path.exists():
        fail(f"Input file not found: {csv_path}")

    rows: List[BudgetRow] = []
    null_rows: List[Dict[str, str]] = []

    try:
        with csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                fail("Input CSV has no header row.")
            missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing:
                fail(f"Input CSV missing required columns: {', '.join(missing)}")

            for raw in reader:
                period = (raw.get("period") or "").strip()
                ward = (raw.get("ward") or "").strip()
                category = (raw.get("category") or "").strip()
                budgeted_str = (raw.get("budgeted_amount") or "").strip()
                actual_str = (raw.get("actual_spend") or "").strip()
                notes = (raw.get("notes") or "").strip()

                if not PERIOD_PATTERN.match(period):
                    fail(
                        f"Invalid period format {period!r}; expected YYYY-MM."
                    )

                budgeted_amount = safe_float(budgeted_str, "budgeted_amount")
                actual_spend: Optional[float]
                if actual_str == "":
                    actual_spend = None
                    null_rows.append(
                        {
                            "period": period,
                            "ward": ward,
                            "category": category,
                            "notes": notes or "No reason provided",
                        }
                    )
                else:
                    actual_spend = safe_float(actual_str, "actual_spend")

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
    except OSError as exc:
        fail(f"Failed to read input CSV: {exc}")

    return {
        "validation_status": "ok",
        "dataset": rows,
        "row_count": len(rows),
        "null_actual_spend_count": len(null_rows),
        "null_rows": null_rows,
    }


def print_null_report(null_rows: List[Dict[str, str]]) -> None:
    print(f"Null actual_spend rows found: {len(null_rows)}")
    if not null_rows:
        return
    for item in null_rows:
        print(
            "- {period} | {ward} | {category} | reason: {notes}".format(
                period=item["period"],
                ward=item["ward"],
                category=item["category"],
                notes=item["notes"],
            )
        )


def build_row_index(rows: List[BudgetRow]) -> Dict[Tuple[str, str, str], BudgetRow]:
    return {(row.period, row.ward, row.category): row for row in rows}


def previous_month(period: str) -> str:
    year = int(period[:4])
    month = int(period[5:7])
    if month == 1:
        return f"{year - 1}-12"
    return f"{year:04d}-{month - 1:02d}"


def previous_year(period: str) -> str:
    year = int(period[:4])
    month = period[5:7]
    return f"{year - 1}-{month}"


def compute_growth(
    rows: List[BudgetRow], ward: str, category: str, growth_type: str
) -> List[Dict[str, str]]:
    filtered = [r for r in rows if r.ward == ward and r.category == category]
    if not filtered:
        fail(f"No rows found for ward={ward!r} and category={category!r}.")

    filtered.sort(key=lambda r: r.period)
    row_index = build_row_index(rows)

    results: List[Dict[str, str]] = []
    label = "MoM" if growth_type == "MOM" else "YoY"

    for row in filtered:
        current = row.actual_spend
        if growth_type == "MOM":
            ref_period = previous_month(row.period)
        else:
            ref_period = previous_year(row.period)

        reference = row_index.get((ref_period, ward, category))
        ref_value = reference.actual_spend if reference else None

        formula = (
            f"(({row.period}_actual - {ref_period}_actual) / {ref_period}_actual) * 100"
        )
        status = "computed"
        note = ""
        growth_value = ""

        if current is None:
            status = "skipped_null"
            note = row.notes or "Current period actual_spend is null"
        elif reference is None:
            status = "skipped_missing_reference"
            note = f"Reference period {ref_period} not available for {label}"
        elif ref_value is None:
            status = "skipped_null_reference"
            note = (
                reference.notes
                or f"Reference period {ref_period} actual_spend is null"
            )
        elif ref_value == 0:
            status = "skipped_zero_reference"
            note = f"Reference period {ref_period} actual_spend is zero"
        else:
            growth = ((current - ref_value) / ref_value) * 100.0
            growth_value = f"{growth:+.1f}%"

        results.append(
            {
                "period": row.period,
                "ward": ward,
                "category": category,
                "actual_spend": "" if current is None else f"{current:.1f}",
                "growth_type": label,
                "growth_value": growth_value,
                "formula": formula,
                "status": status,
                "note": note,
            }
        )

    return results


def write_output(output_path: Path, rows: List[Dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_value",
        "formula",
        "status",
        "note",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()

    ensure_not_aggregate_request(args.ward, "ward")
    ensure_not_aggregate_request(args.category, "category")
    growth_type = normalize_growth_type(args.growth_type)

    payload = load_dataset(Path(args.input))
    null_rows = payload["null_rows"]
    print_null_report(null_rows)

    computed_rows = compute_growth(
        rows=payload["dataset"],
        ward=args.ward.strip(),
        category=args.category.strip(),
        growth_type=growth_type,
    )
    write_output(Path(args.output), computed_rows)
    print(f"Wrote {len(computed_rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
