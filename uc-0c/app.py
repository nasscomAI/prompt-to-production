"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import re
from typing import Dict, List, Optional


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]
VALID_GROWTH_TYPES = {"MoM", "YoY"}


def _is_period(value: str) -> bool:
    return re.match(r"^\d{4}-\d{2}$", value or "") is not None


def load_dataset(input_path: str) -> Dict[str, object]:
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV is missing header row")

        missing_cols = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        rows: List[Dict[str, object]] = []
        null_rows: List[Dict[str, str]] = []
        for row in reader:
            period = (row.get("period") or "").strip()
            if not _is_period(period):
                raise ValueError(f"Invalid period format: {period}")

            budgeted_raw = (row.get("budgeted_amount") or "").strip()
            try:
                budgeted_amount = float(budgeted_raw)
            except ValueError as exc:
                raise ValueError(f"Invalid budgeted_amount '{budgeted_raw}' at {period}") from exc

            actual_raw = (row.get("actual_spend") or "").strip()
            actual_spend: Optional[float]
            if actual_raw == "":
                actual_spend = None
                null_rows.append(
                    {
                        "period": period,
                        "ward": (row.get("ward") or "").strip(),
                        "category": (row.get("category") or "").strip(),
                        "notes": (row.get("notes") or "").strip(),
                    }
                )
            else:
                try:
                    actual_spend = float(actual_raw)
                except ValueError as exc:
                    raise ValueError(f"Invalid actual_spend '{actual_raw}' at {period}") from exc

            rows.append(
                {
                    "period": period,
                    "ward": (row.get("ward") or "").strip(),
                    "category": (row.get("category") or "").strip(),
                    "budgeted_amount": budgeted_amount,
                    "actual_spend": actual_spend,
                    "notes": (row.get("notes") or "").strip(),
                }
            )

    return {
        "rows": rows,
        "schema_validation": {"required_columns": REQUIRED_COLUMNS, "valid": True},
        "null_report": {"null_count": len(null_rows), "null_rows": null_rows},
    }


def compute_growth(rows: List[Dict[str, object]], ward: str, category: str, growth_type: str) -> List[Dict[str, str]]:
    if not ward or ward.strip().lower() in {"all", "*"}:
        raise ValueError("Refused: ward must be a specific ward (all-ward aggregation is not allowed)")
    if not category or category.strip().lower() in {"all", "*"}:
        raise ValueError("Refused: category must be a specific category (all-category aggregation is not allowed)")
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError("Refused: --growth-type must be specified as MoM or YoY")

    scoped = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not scoped:
        raise ValueError("No rows found for requested ward + category")

    scoped.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in scoped}

    output_rows: List[Dict[str, str]] = []
    for idx, current in enumerate(scoped):
        period = str(current["period"])
        curr_actual = current["actual_spend"]
        note = str(current["notes"] or "")

        formula = ""
        growth_percent = ""
        status = "NOT_COMPUTED"
        reason = ""

        if curr_actual is None:
            formula = f"{growth_type} not computed due to null current actual_spend"
            reason = note or "actual_spend is null"
        else:
            comparator = None
            comparator_period = ""

            if growth_type == "MoM":
                if idx == 0:
                    reason = "no previous month available"
                    formula = "MoM requires previous month actual_spend"
                else:
                    prev = scoped[idx - 1]
                    comparator = prev["actual_spend"]
                    comparator_period = str(prev["period"])
            else:
                year, month = period.split("-")
                prev_year_period = f"{int(year) - 1:04d}-{month}"
                prev_year_row = by_period.get(prev_year_period)
                comparator_period = prev_year_period
                comparator = prev_year_row["actual_spend"] if prev_year_row else None
                if prev_year_row is None:
                    reason = "no prior-year same-month row available"
                    formula = "YoY requires same month previous year actual_spend"

            if reason == "":
                if comparator is None:
                    reason = f"comparator actual_spend is null/unavailable for {comparator_period}"
                    formula = f"{growth_type} not computed due to missing comparator"
                elif comparator == 0:
                    reason = f"comparator actual_spend is zero for {comparator_period}"
                    formula = f"(({curr_actual:.2f} - {comparator:.2f}) / {comparator:.2f}) * 100"
                else:
                    formula = f"(({curr_actual:.2f} - {comparator:.2f}) / {comparator:.2f}) * 100"
                    growth = ((float(curr_actual) - float(comparator)) / float(comparator)) * 100.0
                    growth_percent = f"{growth:.1f}%"
                    status = "COMPUTED"
                    reason = ""

        output_rows.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "" if curr_actual is None else f"{float(curr_actual):.1f}",
                "growth_type": growth_type,
                "formula": formula,
                "growth_percent": growth_percent,
                "status": status,
                "reason": reason,
            }
        )

    return output_rows


def _write_output(path: str, rows: List[Dict[str, str]]) -> None:
    fields = [
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
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward")
    parser.add_argument("--category", required=True, help="Target category")
    parser.add_argument("--growth-type", required=False, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    if not args.growth_type:
        raise ValueError("Refused: --growth-type is required (MoM or YoY)")

    loaded = load_dataset(args.input)
    rows = loaded["rows"]
    growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    _write_output(args.output, growth_rows)

    null_report = loaded["null_report"]
    print(
        f"Null rows detected: {null_report['null_count']} | "
        f"Output rows written: {len(growth_rows)}"
    )
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
