"""UC-0C budget growth calculator with strict ward/category scope and MoM rules."""

from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, List, Optional


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

AGGREGATION_TOKENS = {"*", "all", "any", "all wards", "all categories"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute MoM growth for one ward and one category.")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument(
        "--growth-type",
        dest="growth_type",
        required=False,
        help="Growth type. Must be MoM for UC-0C.",
    )
    parser.add_argument("--output", required=True, help="Path to output CSV")
    return parser.parse_args()


def fail(message: str, exit_code: int = 2) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(exit_code)


def parse_optional_float(value: str) -> Optional[float]:
    value = (value or "").strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def is_aggregate_attempt(value: str) -> bool:
    normalized = (value or "").strip().lower()
    return normalized in AGGREGATION_TOKENS


def format_number(value: Optional[float]) -> str:
    if value is None:
        return "NULL"
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    return text if text else "0"


def load_dataset(input_path: str) -> List[Dict[str, object]]:
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                fail("Input CSV has no header row.")
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                fail(f"Input CSV is missing required columns: {', '.join(missing)}")

            rows: List[Dict[str, object]] = []
            null_rows: List[Dict[str, str]] = []

            for raw in reader:
                period = (raw.get("period") or "").strip()
                ward = (raw.get("ward") or "").strip()
                category = (raw.get("category") or "").strip()
                notes = (raw.get("notes") or "").strip()
                actual_value = parse_optional_float(raw.get("actual_spend", ""))

                row: Dict[str, object] = {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual_value,
                    "notes": notes,
                }
                rows.append(row)

                if actual_value is None:
                    null_rows.append(
                        {
                            "period": period,
                            "ward": ward,
                            "category": category,
                            "notes": notes,
                        }
                    )

    except FileNotFoundError:
        fail(f"Input file not found: {input_path}")
    except OSError as exc:
        fail(f"Unable to read input CSV: {exc}")

    print(f"Loaded rows: {len(rows)}")
    print(f"Null actual_spend rows: {len(null_rows)}")
    if null_rows:
        print("Null rows (period, ward, category, notes):")
        for item in null_rows:
            print(
                f"- {item['period']}, {item['ward']}, {item['category']}, {item['notes']}"
            )

    return rows


def compute_growth(
    rows: List[Dict[str, object]], ward: str, category: str
) -> List[Dict[str, object]]:
    if is_aggregate_attempt(ward) or is_aggregate_attempt(category):
        fail("Aggregation across wards/categories is not allowed. Provide one ward and one category.")

    filtered = [
        r for r in rows if str(r.get("ward", "")).strip() == ward and str(r.get("category", "")).strip() == category
    ]
    filtered.sort(key=lambda r: str(r.get("period", "")))

    if not filtered:
        fail("No rows found for the specified ward and category.")

    output: List[Dict[str, object]] = []
    for idx, row in enumerate(filtered):
        current = row.get("actual_spend")
        previous_row = filtered[idx - 1] if idx > 0 else None
        previous = previous_row.get("actual_spend") if previous_row else None

        current_num = float(current) if isinstance(current, (int, float)) else None
        previous_num = float(previous) if isinstance(previous, (int, float)) else None

        formula = (
            f"(({format_number(current_num)} - {format_number(previous_num)}) / "
            f"{format_number(previous_num)}) * 100"
        )

        growth: Optional[float] = None
        flag = ""

        if idx == 0:
            flag = "NO_PREVIOUS_PERIOD"
        elif current_num is None:
            flag_reason = str(row.get("notes") or "NULL actual_spend")
            flag = f"FLAGGED_NULL_CURRENT: {flag_reason}"
        elif previous_num is None:
            prev_reason = str(previous_row.get("notes") or "NULL previous actual_spend")
            flag = f"FLAGGED_NULL_PREVIOUS: {prev_reason}"
        elif previous_num == 0:
            flag = "NON_COMPUTABLE_DIV_BY_ZERO"
        else:
            growth = ((current_num - previous_num) / previous_num) * 100

        output.append(
            {
                "period": row.get("period", ""),
                "ward": row.get("ward", ""),
                "category": row.get("category", ""),
                "actual_spend": "" if current_num is None else format_number(current_num),
                "growth": "" if growth is None else f"{growth:.6f}",
                "formula": formula,
                "flag": flag,
            }
        )

    return output


def write_output(output_path: str, rows: List[Dict[str, object]]) -> None:
    columns = ["period", "ward", "category", "actual_spend", "growth", "formula", "flag"]
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        fail(f"Unable to write output CSV: {exc}")


def main() -> None:
    args = parse_args()

    if not args.growth_type:
        fail("--growth-type is required. Supported value: MoM")
    if args.growth_type != "MoM":
        fail("Only --growth-type MoM is supported for this use case.")

    if is_aggregate_attempt(args.ward) or is_aggregate_attempt(args.category):
        fail("Aggregation across wards/categories is not allowed. Provide one ward and one category.")

    rows = load_dataset(args.input)
    output_rows = compute_growth(rows, args.ward, args.category)
    write_output(args.output, output_rows)
    print(f"Wrote output: {args.output}")


if __name__ == "__main__":
    main()
