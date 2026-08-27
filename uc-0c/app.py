"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from datetime import datetime

REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def _parse_period(period: str) -> datetime:
    return datetime.strptime(period, "%Y-%m")


def _shift_month(period: str, months: int) -> str:
    dt = _parse_period(period)
    year = dt.year
    month = dt.month + months

    while month <= 0:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1

    return f"{year:04d}-{month:02d}"


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    with open(input_path, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV is missing a header row.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Input CSV missing required columns: {', '.join(sorted(missing))}")

        rows: list[dict] = []
        null_rows: list[dict] = []
        for raw in reader:
            budget_raw = (raw.get("budgeted_amount") or "").strip()
            actual_raw = (raw.get("actual_spend") or "").strip()

            try:
                budgeted = float(budget_raw)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid budgeted_amount for {raw.get('period')} {raw.get('ward')} {raw.get('category')}"
                ) from exc

            if actual_raw:
                try:
                    actual = float(actual_raw)
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid actual_spend for {raw.get('period')} {raw.get('ward')} {raw.get('category')}"
                    ) from exc
            else:
                actual = None

            record = {
                "period": (raw.get("period") or "").strip(),
                "ward": (raw.get("ward") or "").strip(),
                "category": (raw.get("category") or "").strip(),
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "notes": (raw.get("notes") or "").strip(),
            }
            rows.append(record)

            if actual is None:
                null_rows.append(
                    {
                        "period": record["period"],
                        "ward": record["ward"],
                        "category": record["category"],
                        "notes": record["notes"] or "No reason provided",
                    }
                )

    rows.sort(key=lambda item: (_parse_period(item["period"]), item["ward"], item["category"]))
    return rows, null_rows


def _validate_scope(ward: str, category: str) -> None:
    invalid_values = {"", "all", "all wards", "all categories", "*"}
    if ward.strip().lower() in invalid_values:
        raise ValueError("Refused: all-ward aggregation is not allowed. Provide one specific --ward.")
    if category.strip().lower() in invalid_values:
        raise ValueError("Refused: all-category aggregation is not allowed. Provide one specific --category.")


def _format_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.1f}"


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    if not growth_type:
        raise ValueError("Refused: --growth-type is required. Specify MoM or YoY explicitly.")

    normalized_growth = growth_type.strip().upper()
    if normalized_growth not in {"MOM", "YOY"}:
        raise ValueError("Invalid --growth-type. Supported values are MoM and YoY.")

    _validate_scope(ward, category)

    scoped_rows = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not scoped_rows:
        raise ValueError("No rows found for the provided ward and category.")

    by_period = {row["period"]: row for row in scoped_rows}
    ordered_periods = sorted(by_period.keys(), key=_parse_period)
    output_rows: list[dict] = []

    for period in ordered_periods:
        current = by_period[period]
        current_actual = current["actual_spend"]

        if normalized_growth == "MOM":
            previous_period = _shift_month(period, -1)
        else:
            previous_period = _shift_month(period, -12)

        previous_row = by_period.get(previous_period)
        previous_actual = previous_row["actual_spend"] if previous_row else None

        formula = f"(({_format_float(current_actual) or 'NULL'} - {_format_float(previous_actual) or 'NULL'}) / {_format_float(previous_actual) or 'NULL'}) * 100"

        status = "NOT_COMPUTED"
        growth_percent = ""
        null_flag = ""
        null_reason = ""

        if current_actual is None:
            null_flag = "NULL_INPUT"
            null_reason = current["notes"] or "No reason provided"
            status = "CURRENT_NULL"
        elif previous_row is None:
            status = "BASE_PERIOD_MISSING"
        elif previous_actual is None:
            status = "BASE_PERIOD_NULL"
        elif previous_actual == 0:
            status = "BASE_PERIOD_ZERO"
        else:
            growth_value = ((current_actual - previous_actual) / previous_actual) * 100.0
            growth_percent = f"{growth_value:+.1f}%"
            status = "COMPUTED"

        output_rows.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": f"{current['budgeted_amount']:.1f}",
                "actual_spend": _format_float(current_actual),
                "previous_period": previous_period,
                "previous_actual_spend": _format_float(previous_actual),
                "growth_type": normalized_growth,
                "growth_percent": growth_percent,
                "formula": formula,
                "null_flag": null_flag,
                "null_reason": null_reason,
                "status": status,
            }
        )

    return output_rows


def write_growth_output(output_path: str, rows: list[dict]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "previous_period",
        "previous_actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "null_flag",
        "null_reason",
        "status",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", required=False, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    print("Null rows detected before computation:")
    for row in null_rows:
        print(
            f"- {row['period']} | {row['ward']} | {row['category']} | reason: {row['notes']}"
        )

    growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_growth_output(args.output, growth_rows)

    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()
