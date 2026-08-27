"""
UC-0C app.py — Number That Looks Right
Reads ward budget spend, flags null rows, and computes per-period growth
for one ward and category only. It refuses to aggregate across wards or
categories and requires an explicit growth type.
"""
import argparse
import csv
import datetime
import os
from typing import Dict, List, Optional

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = {"MOM", "YOY"}


def parse_period(period_text: str) -> datetime.date:
    try:
        year_text, month_text = period_text.split("-")
        year = int(year_text)
        month = int(month_text)
        return datetime.date(year, month, 1)
    except Exception as exc:
        raise ValueError(f"Invalid period format: {period_text}") from exc


def shift_month(period_date: datetime.date, months: int) -> datetime.date:
    total_months = period_date.year * 12 + period_date.month - 1 + months
    year = total_months // 12
    month = (total_months % 12) + 1
    return datetime.date(year, month, 1)


def load_dataset(input_path: str) -> List[Dict]:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")

        missing_columns = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"Missing required CSV columns: {missing_columns}")

        rows = []
        for line_number, raw_row in enumerate(reader, start=2):
            row = {key: (raw_row.get(key, "") or "").strip() for key in REQUIRED_COLUMNS}
            period = row["period"]
            if not period:
                raise ValueError(f"Missing period on line {line_number}.")

            try:
                row["period_date"] = parse_period(period)
            except ValueError as exc:
                raise ValueError(f"Invalid period on line {line_number}: {period}") from exc

            try:
                row["budgeted_amount"] = float(row["budgeted_amount"])
            except ValueError:
                raise ValueError(f"Invalid budgeted_amount on line {line_number}: {row['budgeted_amount']}")

            actual_text = row["actual_spend"]
            row["actual_spend"] = None if actual_text == "" else float(actual_text)
            row["notes"] = row["notes"]
            rows.append(row)

    null_rows = [r for r in rows if r["actual_spend"] is None]
    print(f"Loaded {len(rows)} rows from {input_path}.")
    print(f"Found {len(null_rows)} null actual_spend rows.")
    for row in null_rows:
        print(
            f"- {row['period']} · {row['ward']} · {row['category']} · reason: {row['notes'] or 'no notes'}"
        )

    return rows


def format_growth_percentage(change: float, base: float) -> str:
    return f"{change / base:+.1%}"


def compute_growth(
    data: List[Dict], ward: str, category: str, growth_type: str
) -> List[Dict]:
    growth_type_key = growth_type.upper()
    if growth_type_key not in VALID_GROWTH_TYPES:
        raise ValueError(f"Unsupported growth type '{growth_type}'. Choose one of: {', '.join(VALID_GROWTH_TYPES)}")

    rows = [r for r in data if r["ward"] == ward and r["category"] == category]
    if not rows:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'.")

    rows.sort(key=lambda item: item["period_date"])
    row_by_period = {row["period"]: row for row in rows}
    output = []

    for row in rows:
        row_output = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": "" if row["actual_spend"] is None else f"{row['actual_spend']:.1f}",
            "growth_type": growth_type_key,
            "formula": "",
            "growth_pct": "",
            "status": "",
            "notes": row["notes"],
        }

        if row["actual_spend"] is None:
            row_output["status"] = "NULL - flagged"
            row_output["notes"] = row["notes"] or "actual_spend is missing"
            output.append(row_output)
            continue

        if growth_type_key == "MOM":
            prior_date = shift_month(row["period_date"], -1)
        else:
            prior_date = shift_month(row["period_date"], -12)

        prior_period = prior_date.strftime("%Y-%m")
        prior_row = row_by_period.get(prior_period)

        if prior_row is None:
            row_output["status"] = f"Missing prior period for {growth_type_key}"
            row_output["notes"] = f"Cannot compute {growth_type_key} growth without prior period row {prior_period}."
        elif prior_row["actual_spend"] is None:
            row_output["status"] = f"Prior period has NULL actual_spend"
            row_output["notes"] = f"Cannot compute {growth_type_key} growth because {prior_period} actual_spend is null."
        elif prior_row["actual_spend"] == 0:
            row_output["status"] = "Prior period actual_spend is zero"
            row_output["notes"] = "Cannot compute growth when prior actual_spend is zero."
        else:
            current = row["actual_spend"]
            prior = prior_row["actual_spend"]
            change = current - prior
            row_output["formula"] = f"({current:.1f} - {prior:.1f}) / {prior:.1f}"
            row_output["growth_pct"] = format_growth_percentage(change, prior)
            row_output["status"] = "OK"
            row_output["notes"] = row["notes"] or ""

        output.append(row_output)

    return output


def write_output(output_path: str, rows: List[Dict]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_pct",
        "status",
        "notes",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Compute per-ward, per-category budget growth from actual spend.")
    parser.add_argument("--input", required=True, help="Path to the ward budget CSV input file.")
    parser.add_argument("--ward", required=True, help="Ward name to compute growth for.")
    parser.add_argument("--category", required=True, help="Category name to compute growth for.")
    parser.add_argument("--growth-type", required=True, help="Growth type to compute: MoM or YoY.")
    parser.add_argument("--output", required=True, help="Path to write the growth output CSV.")
    args = parser.parse_args()

    try:
        dataset = load_dataset(args.input)
        growth_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
        write_output(args.output, growth_rows)
        print(f"Done. Growth results written to {args.output}")
    except Exception as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
