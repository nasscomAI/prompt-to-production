"""
UC-0C app.py — Number That Looks Right
Built via RICE -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(csv_path: str):
    """
    Reads the budget CSV, validates columns, reports null actual_spend rows.
    Returns: (rows, null_report)
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Required column(s) missing from {csv_path}: {missing}")
        rows = list(reader)

    null_report = [
        {"period": r["period"], "ward": r["ward"], "category": r["category"], "notes": r["notes"]}
        for r in rows
        if not r["actual_spend"].strip()
    ]
    return rows, null_report


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Returns a per-period table for the given ward+category, formula shown per row.
    growth_type must be 'MoM' or 'YoY'.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError("growth_type must be specified as 'MoM' or 'YoY' — refusing to guess.")

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        raise ValueError(f"No rows found for ward={ward!r} category={category!r} — refusing to aggregate across others.")

    by_period = {r["period"]: r for r in filtered}
    results = []

    for row in filtered:
        period = row["period"]
        raw_spend = row["actual_spend"].strip()

        if not raw_spend:
            results.append({
                "period": period,
                "actual_spend": None,
                "formula": f"NOT COMPUTED — null actual_spend ({row['notes']})",
                "growth_pct": None,
            })
            continue

        actual_spend = float(raw_spend)

        if growth_type == "MoM":
            prev_period = _shift_month(period, -1)
        else:
            prev_period = _shift_year(period, -1)

        prev_row = by_period.get(prev_period)
        prev_spend = prev_row["actual_spend"].strip() if prev_row else ""

        if not prev_row or not prev_spend:
            reason = "no prior-period data in range" if not prev_row else f"prior period null ({prev_row['notes']})"
            results.append({
                "period": period,
                "actual_spend": actual_spend,
                "formula": f"NOT COMPUTED — {reason}",
                "growth_pct": None,
            })
            continue

        prev_val = float(prev_spend)
        growth_pct = round((actual_spend - prev_val) / prev_val * 100, 1)
        results.append({
            "period": period,
            "actual_spend": actual_spend,
            "formula": f"{growth_type} = (actual_spend[{period}] - actual_spend[{prev_period}]) / actual_spend[{prev_period}] = ({actual_spend} - {prev_val}) / {prev_val}",
            "growth_pct": growth_pct,
        })

    return results


def _shift_month(period: str, delta: int) -> str:
    year, month = (int(p) for p in period.split("-"))
    total = year * 12 + (month - 1) + delta
    new_year, new_month = divmod(total, 12)
    return f"{new_year:04d}-{new_month + 1:02d}"


def _shift_year(period: str, delta: int) -> str:
    year, month = period.split("-")
    return f"{int(year) + delta:04d}-{month}"


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", default=None, help="MoM or YoY — no default, must be specified")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    if args.growth_type not in ("MoM", "YoY"):
        print(
            "REFUSED: --growth-type not specified or invalid. "
            "You must explicitly pass --growth-type MoM or --growth-type YoY — this cannot be guessed.",
            file=sys.stderr,
        )
        sys.exit(1)

    rows, null_report = load_dataset(args.input)

    if null_report:
        print(f"NULL REPORT — {len(null_report)} row(s) with missing actual_spend:")
        for entry in null_report:
            print(f"  {entry['period']} · {entry['ward']} · {entry['category']} — {entry['notes']}")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "formula", "growth_pct"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"Done. Growth table for {args.ward} / {args.category} ({args.growth_type}) written to {args.output}")


if __name__ == "__main__":
    main()
