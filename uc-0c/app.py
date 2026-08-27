"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
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

MOM_FORMULA = "MoM: ((current_actual_spend - previous_actual_spend) / previous_actual_spend) * 100"
YOY_FORMULA = "YoY: ((current_actual_spend - same_month_last_year_actual_spend) / same_month_last_year_actual_spend) * 100"


def _parse_period(period: str) -> datetime:
    return datetime.strptime(period, "%Y-%m")


def _to_float_or_none(value: str) -> Optional[float]:
    if value is None:
        return None
    text = value.strip()
    if text == "":
        return None
    return float(text)


def load_dataset(input_path: str) -> Tuple[List[Dict[str, object]], List[Dict[str, str]]]:
    """
    Load CSV, validate columns, and report rows with null actual_spend.
    Returns:
      - parsed rows
      - list of null rows metadata
    """
    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        headers = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        rows: List[Dict[str, object]] = []
        null_rows: List[Dict[str, str]] = []

        for raw in reader:
            actual = _to_float_or_none((raw.get("actual_spend") or ""))
            parsed = {
                "period": (raw.get("period") or "").strip(),
                "ward": (raw.get("ward") or "").strip(),
                "category": (raw.get("category") or "").strip(),
                "budgeted_amount": _to_float_or_none((raw.get("budgeted_amount") or "")),
                "actual_spend": actual,
                "notes": (raw.get("notes") or "").strip(),
            }
            rows.append(parsed)

            if actual is None:
                null_rows.append(
                    {
                        "period": str(parsed["period"]),
                        "ward": str(parsed["ward"]),
                        "category": str(parsed["category"]),
                        "notes": str(parsed["notes"]),
                    }
                )

    return rows, null_rows


def compute_growth(
    rows: List[Dict[str, object]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    """
    Compute growth for one ward+category scope only.
    Returns one row per period with formula and null flags.
    """
    scope_rows = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not scope_rows:
        raise ValueError("No rows found for the requested ward and category scope.")

    scope_rows.sort(key=lambda r: _parse_period(str(r["period"])))

    growth = growth_type.strip().lower()
    if growth == "mom":
        formula_used = MOM_FORMULA
    elif growth == "yoy":
        formula_used = YOY_FORMULA
    else:
        raise ValueError("Invalid growth_type. Use MoM or YoY.")

    by_period = {str(r["period"]): r for r in scope_rows}
    output: List[Dict[str, str]] = []

    for idx, current in enumerate(scope_rows):
        period = str(current["period"])
        current_actual = current["actual_spend"]
        current_notes = str(current["notes"])

        record = {
            "period": period,
            "ward": str(current["ward"]),
            "category": str(current["category"]),
            "actual_spend": "" if current_actual is None else f"{float(current_actual):.1f}",
            "growth_type": growth.upper(),
            "growth_value": "",
            "formula_used": formula_used,
            "null_flag": "",
            "null_reason": "",
        }

        if current_actual is None:
            record["null_flag"] = "NEEDS_REVIEW"
            record["null_reason"] = current_notes or "actual_spend missing"
            output.append(record)
            continue

        base_actual: Optional[float] = None
        base_missing_reason = ""

        if growth == "mom":
            if idx == 0:
                base_missing_reason = "No previous period available"
            else:
                previous = scope_rows[idx - 1]
                base_actual = previous["actual_spend"]  # type: ignore[assignment]
                if base_actual is None:
                    base_missing_reason = str(previous["notes"]) or "previous period actual_spend missing"
        else:  # YoY
            dt = _parse_period(period)
            prev_year_period = f"{dt.year - 1:04d}-{dt.month:02d}"
            previous = by_period.get(prev_year_period)
            if previous is None:
                base_missing_reason = "No same month in previous year"
            else:
                base_actual = previous["actual_spend"]  # type: ignore[assignment]
                if base_actual is None:
                    base_missing_reason = str(previous["notes"]) or "same month last year actual_spend missing"

        if base_actual is None:
            record["null_flag"] = "NEEDS_REVIEW"
            record["null_reason"] = base_missing_reason
        elif base_actual == 0:
            record["null_flag"] = "NEEDS_REVIEW"
            record["null_reason"] = "Base period actual_spend is 0; growth undefined"
        else:
            growth_value = ((float(current_actual) - float(base_actual)) / float(base_actual)) * 100
            record["growth_value"] = f"{growth_value:.1f}%"

        output.append(record)

    return output


def _is_aggregate_request(value: str) -> bool:
    val = value.strip().lower()
    return val in {"all", "*", "any", "all wards", "all categories"}


def main():
    parser = argparse.ArgumentParser(description="UC-0C ward/category growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    if not args.growth_type:
        raise SystemExit("Refused: --growth-type is required. Please specify MoM or YoY.")

    if _is_aggregate_request(args.ward) or _is_aggregate_request(args.category):
        raise SystemExit(
            "Refused: aggregation across wards/categories is not allowed by default. Provide one exact --ward and one exact --category."
        )

    rows, null_rows = load_dataset(args.input)
    print(f"Loaded {len(rows)} rows. Found {len(null_rows)} rows with null actual_spend.")
    if null_rows:
        print("Null rows detected (period | ward | category | notes):")
        for item in null_rows:
            print(
                f"- {item['period']} | {item['ward']} | {item['category']} | {item['notes']}"
            )

    result_rows = compute_growth(
        rows=rows,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
    )

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_value",
        "formula_used",
        "null_flag",
        "null_reason",
    ]

    with open(args.output, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result_rows)

    print(f"Done. Wrote {len(result_rows)} rows to {args.output}")

if __name__ == "__main__":
    main()
