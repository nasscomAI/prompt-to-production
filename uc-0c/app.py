"""
UC-0C -- Number That Looks Right.

Computes growth only for one explicit ward/category slice and reports null
actual_spend rows before any calculation.
"""
import argparse
import csv
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

SUPPORTED_GROWTH_TYPES = {"MoM", "YoY"}


def parse_money(value, column_name, row_number):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        raise ValueError(f"Row {row_number}: invalid {column_name!r} value {value!r}")


def fmt_decimal(value):
    if value is None:
        return ""
    return format(value.normalize(), "f")


def fmt_growth(value):
    if value is None:
        return ""
    rounded = value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    sign = "+" if rounded > 0 else ""
    return f"{sign}{rounded}%"


def load_dataset(input_path):
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"Input CSV missing required columns: {', '.join(sorted(missing))}")

        rows = []
        null_rows = []
        for index, row in enumerate(reader, start=2):
            normalized = {key: (value or "").strip() for key, value in row.items()}
            normalized["source_row"] = index
            normalized["budgeted_amount"] = parse_money(
                normalized["budgeted_amount"], "budgeted_amount", index
            )
            normalized["actual_spend"] = (
                None
                if normalized["actual_spend"] == ""
                else parse_money(normalized["actual_spend"], "actual_spend", index)
            )
            rows.append(normalized)

            if normalized["actual_spend"] is None:
                null_rows.append(normalized)

    print(f"Null actual_spend rows found before computing: {len(null_rows)}")
    for row in null_rows:
        print(
            "NULL actual_spend | "
            f"period={row['period']} | ward={row['ward']} | "
            f"category={row['category']} | reason={row['notes']}"
        )

    return rows


def period_to_previous(period, growth_type):
    year_text, month_text = period.split("-", 1)
    year = int(year_text)
    month = int(month_text)

    if growth_type == "MoM":
        if month == 1:
            return f"{year - 1}-12"
        return f"{year}-{month - 1:02d}"

    if growth_type == "YoY":
        return f"{year - 1}-{month:02d}"

    raise ValueError(f"Unsupported growth type: {growth_type}")


def compute_growth(rows, ward, category, growth_type):
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        allowed = ", ".join(sorted(SUPPORTED_GROWTH_TYPES))
        raise ValueError(f"Unsupported --growth-type {growth_type!r}. Use one of: {allowed}")

    selected = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]
    if not selected:
        raise ValueError(f"No rows found for ward={ward!r}, category={category!r}")

    selected.sort(key=lambda row: row["period"])
    by_period = {row["period"]: row for row in selected}
    output_rows = []

    for row in selected:
        previous_period = period_to_previous(row["period"], growth_type)
        previous = by_period.get(previous_period)
        current_actual = row["actual_spend"]
        previous_actual = previous["actual_spend"] if previous else None
        formula = (
            f"(({row['period']} actual_spend - {previous_period} actual_spend) "
            f"/ {previous_period} actual_spend) * 100"
        )

        growth = None
        status = "computed"
        reason = ""

        if current_actual is None:
            status = "not_computed"
            reason = f"current actual_spend is NULL: {row['notes']}"
        elif previous is None:
            status = "not_computed"
            reason = f"comparison period {previous_period} is not present"
        elif previous_actual is None:
            status = "not_computed"
            reason = f"comparison period actual_spend is NULL: {previous['notes']}"
        elif previous_actual == 0:
            status = "not_computed"
            reason = f"comparison period {previous_period} actual_spend is zero"
        else:
            growth = ((current_actual - previous_actual) / previous_actual) * Decimal("100")

        output_rows.append(
            {
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "growth_type": growth_type,
                "actual_spend": fmt_decimal(current_actual),
                "comparison_period": previous_period,
                "comparison_actual_spend": fmt_decimal(previous_actual),
                "growth_percent": fmt_growth(growth),
                "formula": formula,
                "status": status,
                "null_reason": row["notes"] if current_actual is None else "",
                "message": reason,
            }
        )

    return output_rows


def write_output(output_path, rows):
    fieldnames = [
        "period",
        "ward",
        "category",
        "growth_type",
        "actual_spend",
        "comparison_period",
        "comparison_actual_spend",
        "growth_percent",
        "formula",
        "status",
        "null_reason",
        "message",
    ]
    with Path(output_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Compute explicit per-ward, per-category budget growth."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exact ward name to compute")
    parser.add_argument("--category", help="Exact category name to compute")
    parser.add_argument("--growth-type", help="Required growth formula, e.g. MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV path")
    return parser


def validate_args(args, parser):
    if not args.growth_type:
        parser.error("Refusing to guess formula: provide --growth-type, for example MoM.")
    if not args.ward or not args.category:
        parser.error(
            "Refusing all-ward/all-category aggregation: provide both --ward and --category."
        )


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_args(args, parser)

    try:
        rows = load_dataset(args.input)
        output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
        write_output(args.output, output_rows)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"Wrote {len(output_rows)} per-period rows for ward={args.ward!r}, "
        f"category={args.category!r} to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
