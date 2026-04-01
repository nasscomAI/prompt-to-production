"""
UC-0C app.py — Budget Growth Calculator
Computes MoM or YoY actual-spend growth for a specified ward and category.
Enforces per-ward per-category scope and flags all null rows before computing.
"""
import argparse
import csv
import sys


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str) -> tuple:
    """
    Read ward_budget.csv, validate columns, report null rows.
    Returns (rows, null_report) where rows is a list of dicts.
    """
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file appears to be empty or has no header row.")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        rows = list(reader)

    null_rows = [
        {
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "notes": r["notes"],
        }
        for r in rows
        if r["actual_spend"].strip() == ""
    ]

    null_report = {
        "null_count": len(null_rows),
        "null_rows": null_rows,
    }
    return rows, null_report


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute MoM or YoY growth for the specified ward and category.
    Null rows are flagged; computation is skipped for those rows.
    Returns list of dicts: period, actual_spend, growth_pct, formula.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"growth_type must be 'MoM' or 'YoY', got '{growth_type}'. "
            "Please specify --growth-type MoM or --growth-type YoY."
        )

    # Filter to the exact ward and category
    subset = [
        r for r in rows
        if r["ward"].strip() == ward.strip()
        and r["category"].strip() == category.strip()
    ]
    if not subset:
        wards = sorted({r["ward"] for r in rows})
        cats = sorted({r["category"] for r in rows})
        raise ValueError(
            f"No rows found for ward='{ward}', category='{category}'.\n"
            f"Available wards: {wards}\nAvailable categories: {cats}"
        )

    # Sort by period
    subset.sort(key=lambda r: r["period"])

    # Build lookup from period to actual_spend (or None)
    def parse_spend(s: str):
        s = s.strip()
        if s == "":
            return None
        return float(s)

    results = []
    for i, row in enumerate(subset):
        period = row["period"]
        notes = row["notes"].strip()
        spend = parse_spend(row["actual_spend"])

        if growth_type == "MoM":
            # Previous period = one month earlier in the same ward/category
            prev_row = subset[i - 1] if i > 0 else None
            prev_spend = parse_spend(prev_row["actual_spend"]) if prev_row else None
            prev_period = prev_row["period"] if prev_row else None
        else:  # YoY
            # Previous period = same month, one year earlier
            year, month = period.split("-")
            prev_period_key = f"{int(year) - 1}-{month}"
            prev_rows = [r for r in subset if r["period"] == prev_period_key]
            prev_row = prev_rows[0] if prev_rows else None
            prev_spend = parse_spend(prev_row["actual_spend"]) if prev_row else None
            prev_period = prev_row["period"] if prev_row else None

        # Determine growth
        if spend is None:
            growth_pct = f"NULL — {notes if notes else 'actual_spend missing'}"
            formula = "Cannot compute — actual_spend is NULL"
        elif prev_spend is None or prev_period is None:
            growth_pct = "N/A — no prior period available"
            formula = f"No {growth_type} baseline available"
        elif prev_spend == 0:
            growth_pct = "N/A — prior period spend is zero (division by zero)"
            formula = f"({spend} - {prev_spend}) / {prev_spend} × 100 = undefined"
        else:
            pct = (spend - prev_spend) / prev_spend * 100
            sign = "+" if pct >= 0 else ""
            growth_pct = f"{sign}{pct:.1f}%"
            formula = (
                f"{growth_type}: ({spend} - {prev_spend}) / {prev_spend} × 100 "
                f"= {sign}{pct:.1f}%"
            )

        results.append({
            "period": period,
            "actual_spend": spend if spend is not None else "NULL",
            "growth_pct": growth_pct,
            "formula": formula,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact)")
    parser.add_argument("--category", required=True, help="Spending category (exact)")
    parser.add_argument(
        "--growth-type", required=True,
        choices=["MoM", "YoY"],
        help="Growth type: MoM (month-over-month) or YoY (year-over-year)"
    )
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)

    print(f"Dataset loaded: {len(rows)} rows total.")
    print(f"NULL actual_spend rows found: {null_report['null_count']}")
    for nr in null_report["null_rows"]:
        print(f"  NULL: {nr['period']} | {nr['ward']} | {nr['category']} | {nr['notes']}")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["period", "actual_spend", "growth_pct", "formula"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nGrowth output written to {args.output} ({len(results)} rows).")
    print(f"Scope: ward='{args.ward}', category='{args.category}', type={args.growth_type}")


if __name__ == "__main__":
    main()
