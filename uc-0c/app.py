"""
UC-0C — Number That Looks Right
Budget Growth Calculator

Computes period-over-period growth rates for a specific ward and category.
Enforcement rules:
  1. Never aggregate across wards or categories
  2. Flag every null row before computing
  3. Show formula in every output row
  4. Refuse if --growth-type not specified
"""

import argparse
import csv
import sys


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Compute budget growth rates per ward per category."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Budget category to filter")
    parser.add_argument(
        "--growth-type",
        required=False,
        default=None,
        help="Growth type: MoM (month-over-month) or YoY (year-over-year)",
    )
    parser.add_argument("--output", required=True, help="Output CSV file path")
    return parser.parse_args()


def load_dataset(filepath, ward, category):
    """
    Load ward_budget.csv and filter to specified ward and category.
    Returns sorted list of row dicts with actual_spend as float or None.
    """
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ward"].strip() == ward and row["category"].strip() == category:
                spend = row["actual_spend"].strip()
                rows.append(
                    {
                        "period": row["period"].strip(),
                        "ward": row["ward"].strip(),
                        "category": row["category"].strip(),
                        "budgeted_amount": float(row["budgeted_amount"].strip()),
                        "actual_spend": float(spend) if spend else None,
                        "notes": row["notes"].strip() if row["notes"] else "",
                    }
                )
    # Sort by period (YYYY-MM lexicographic sort is chronological)
    rows.sort(key=lambda r: r["period"])
    return rows


def compute_growth(rows, growth_type):
    """
    Compute period-over-period growth rates.
    Returns list of result dicts with: period, ward, category, actual_spend,
    growth_pct, formula, flag.
    """
    if growth_type not in ("MoM", "YoY"):
        print(
            f"ERROR: Invalid growth type '{growth_type}'. Must be 'MoM' or 'YoY'.",
            file=sys.stderr,
        )
        sys.exit(1)

    results = []

    for i, row in enumerate(rows):
        result = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": row["actual_spend"] if row["actual_spend"] is not None else "",
            "growth_pct": "",
            "formula": "",
            "flag": "",
        }

        # First row — no previous value
        if i == 0:
            results.append(result)
            continue

        # Current row has null actual_spend
        if row["actual_spend"] is None:
            reason = row["notes"] if row["notes"] else "No reason provided"
            result["flag"] = f"NULL - {reason}"
            results.append(result)
            continue

        # Previous row had null actual_spend
        if rows[i - 1]["actual_spend"] is None:
            result["flag"] = "PREV_NULL"
            results.append(result)
            continue

        # Normal computation
        current = row["actual_spend"]
        previous = rows[i - 1]["actual_spend"]

        if previous == 0:
            result["growth_pct"] = ""
            result["formula"] = "Division by zero — previous period is 0"
            result["flag"] = "DIV_ZERO"
        else:
            growth_pct = round(((current - previous) / previous) * 100, 1)
            result["growth_pct"] = growth_pct
            result["formula"] = (
                f"({current} - {previous}) / {previous} * 100 = {growth_pct}%"
            )

        results.append(result)

    return results


def write_output(results, output_path):
    """Write results to CSV."""
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    args = parse_args()

    # Enforcement: refuse if --growth-type not specified
    if args.growth_type is None:
        print(
            "ERROR: --growth-type is required. Please specify 'MoM' (month-over-month) "
            "or 'YoY' (year-over-year). I will not guess a default.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.growth_type not in ("MoM", "YoY"):
        print(
            f"ERROR: Invalid --growth-type '{args.growth_type}'. "
            "Must be 'MoM' or 'YoY'.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load and filter data — single ward, single category only
    rows = load_dataset(args.input, args.ward, args.category)

    if not rows:
        print(
            f"ERROR: No data found for ward='{args.ward}', category='{args.category}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Report null rows before computation
    null_rows = [r for r in rows if r["actual_spend"] is None]
    if null_rows:
        print(f"\n⚠️  Found {len(null_rows)} null actual_spend row(s):")
        for r in null_rows:
            reason = r["notes"] if r["notes"] else "No reason provided"
            print(f"   • {r['period']} | {r['ward']} | {r['category']} | Reason: {reason}")
        print()

    # Compute growth
    results = compute_growth(rows, args.growth_type)

    # Write output
    write_output(results, args.output)

    print(f"✅ Growth output written to: {args.output}")
    print(f"   Ward: {args.ward}")
    print(f"   Category: {args.category}")
    print(f"   Growth type: {args.growth_type}")
    print(f"   Rows: {len(results)}")


if __name__ == "__main__":
    main()
