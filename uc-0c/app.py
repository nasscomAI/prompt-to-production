"""
UC-0C app.py
Built using the RICE (agents.md) -> skills.md -> CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from datetime import datetime

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = ("MoM", "YoY")
NO_REASON = "no reason given"


def load_dataset(input_path: str) -> list:
    """
    Read the ward budget CSV, validate columns, and report null actual_spend
    rows (with their notes reason) before returning the dataset.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Input CSV is missing required columns: {missing}")
        rows = list(reader)

    null_rows = [r for r in rows if not r["actual_spend"].strip()]
    print(f"Loaded {len(rows)} rows. {len(null_rows)} rows have a null actual_spend:")
    for r in null_rows:
        reason = r["notes"].strip() or NO_REASON
        print(f"  - {r['period']} | {r['ward']} | {r['category']} | reason: {reason}")

    return rows


def _period_key(period: str) -> datetime:
    return datetime.strptime(period, "%Y-%m")


def _prev_period_for(period: str, growth_type: str) -> str:
    current_dt = _period_key(period)
    if growth_type == "MoM":
        prev_year = current_dt.year if current_dt.month > 1 else current_dt.year - 1
        prev_month = current_dt.month - 1 if current_dt.month > 1 else 12
    else:  # YoY
        prev_year = current_dt.year - 1
        prev_month = current_dt.month
    return f"{prev_year:04d}-{prev_month:02d}"


def _base_entry(row: dict, ward: str, category: str, growth_type: str) -> dict:
    current_spend_raw = row["actual_spend"].strip()
    return {
        "period": row["period"],
        "ward": ward,
        "category": category,
        "growth_type": growth_type,
        "actual_spend": current_spend_raw or "NULL",
        "growth_pct": "",
        "formula": "",
        "flag": "",
    }


def _compute_row_growth(row: dict, by_period: dict, ward: str, category: str, growth_type: str) -> dict:
    period = row["period"]
    prev_period = _prev_period_for(period, growth_type)
    prev_row = by_period.get(prev_period)
    entry = _base_entry(row, ward, category, growth_type)

    current_spend_raw = row["actual_spend"].strip()
    if not current_spend_raw:
        reason = row["notes"].strip() or NO_REASON
        entry["flag"] = f"NOT_COMPUTED — actual_spend is null ({reason})"
        return entry

    if prev_row is None:
        entry["flag"] = f"NOT_COMPUTED — no {prev_period} data in dataset for this ward/category"
        return entry

    prev_spend_raw = prev_row["actual_spend"].strip()
    if not prev_spend_raw:
        reason = prev_row["notes"].strip() or NO_REASON
        entry["flag"] = f"NOT_COMPUTED — prior period {prev_period} actual_spend is null ({reason})"
        return entry

    current_spend = float(current_spend_raw)
    prev_spend = float(prev_spend_raw)
    growth = (current_spend - prev_spend) / prev_spend
    entry["growth_pct"] = f"{growth * 100:+.1f}%"
    entry["formula"] = f"({current_spend} - {prev_spend}) / {prev_spend} [period {period} vs {prev_period}]"
    return entry


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for exactly one ward + category.
    Every computed row shows its formula; every row that cannot be computed
    is flagged with the specific reason instead of being guessed.
    """
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(f"--growth-type must be one of {VALID_GROWTH_TYPES}, got {growth_type!r}")

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No rows found for ward={ward!r}, category={category!r}")

    filtered.sort(key=lambda r: _period_key(r["period"]))
    by_period = {r["period"]: r for r in filtered}

    return [_compute_row_growth(row, by_period, ward, category, growth_type) for row in filtered]


def main():
    parser = argparse.ArgumentParser(description="UC-0C Spend Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Exact category name, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=True, choices=list(VALID_GROWTH_TYPES),
                         help="MoM or YoY — required, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if args.ward.strip().lower() in ("all", "*", "all wards"):
        raise ValueError("Aggregation across all wards is refused — specify one exact ward.")
    if args.category.strip().lower() in ("all", "*", "all categories"):
        raise ValueError("Aggregation across all categories is refused — specify one exact category.")

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "growth_type", "actual_spend", "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
