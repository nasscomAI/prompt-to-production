"""
UC-0C app.py — Budget growth analysis per ward per category.
Computes MoM or YoY growth from ward_budget.csv with null-row flagging.
"""
import argparse
import csv
import sys


VALID_GROWTH_TYPES = {"MoM", "YoY"}


def load_dataset(path, ward, category):
    """Reads CSV, validates columns, filters to ward+category, reports nulls."""
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows = []
    null_rows = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not required_columns.issubset(set(reader.fieldnames or [])):
            missing = required_columns - set(reader.fieldnames or [])
            print(f"ERROR: Missing columns in CSV: {missing}", file=sys.stderr)
            sys.exit(1)

        for row in reader:
            if row["ward"] == ward and row["category"] == category:
                if row["actual_spend"].strip() == "":
                    null_rows.append(row)
                else:
                    row["actual_spend"] = float(row["actual_spend"])
                    rows.append(row)

    if not rows and not null_rows:
        print(f"ERROR: No data found for ward='{ward}' category='{category}'", file=sys.stderr)
        sys.exit(1)

    if null_rows:
        print(f"\nNULL ROWS DETECTED — excluded from growth computation:")
        for nr in null_rows:
            reason = nr["notes"].strip() or "no reason given"
            print(f"  period={nr['period']}  ward={nr['ward']}  category={nr['category']}  reason: {reason}")
        print()

    # Sort by period
    rows.sort(key=lambda r: r["period"])
    return rows, null_rows


def compute_growth(rows, growth_type):
    """Returns per-period table with growth value and formula shown."""
    results = []

    if growth_type == "MoM":
        for i, row in enumerate(rows):
            if i == 0:
                results.append({
                    "period": row["period"],
                    "actual_spend": row["actual_spend"],
                    "growth": "N/A",
                    "formula": "first period — no prior month",
                })
            else:
                prev = rows[i - 1]
                prev_spend = prev["actual_spend"]
                curr_spend = row["actual_spend"]
                pct = ((curr_spend - prev_spend) / prev_spend) * 100
                sign = "+" if pct >= 0 else ""
                results.append({
                    "period": row["period"],
                    "actual_spend": curr_spend,
                    "growth": f"{sign}{pct:.1f}%",
                    "formula": f"({curr_spend} - {prev_spend}) / {prev_spend} × 100",
                })

    elif growth_type == "YoY":
        # Build period → spend lookup
        spend_map = {r["period"]: r["actual_spend"] for r in rows}
        for row in rows:
            period = row["period"]
            year, month = period.split("-")
            prior_period = f"{int(year) - 1}-{month}"
            curr_spend = row["actual_spend"]
            if prior_period in spend_map:
                prev_spend = spend_map[prior_period]
                pct = ((curr_spend - prev_spend) / prev_spend) * 100
                sign = "+" if pct >= 0 else ""
                results.append({
                    "period": period,
                    "actual_spend": curr_spend,
                    "growth": f"{sign}{pct:.1f}%",
                    "formula": f"({curr_spend} - {prev_spend}) / {prev_spend} × 100  [vs {prior_period}]",
                })
            else:
                results.append({
                    "period": period,
                    "actual_spend": curr_spend,
                    "growth": "N/A",
                    "formula": f"no data for prior-year period {prior_period}",
                })

    return results


def main():
    parser = argparse.ArgumentParser(description="Ward budget growth analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category to filter")
    parser.add_argument("--growth-type", required=True, choices=list(VALID_GROWTH_TYPES),
                        help="Growth type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    print(f"Loading dataset: {args.input}")
    print(f"Filter — ward: {args.ward}  category: {args.category}  growth-type: {args.growth_type}")

    rows, null_rows = load_dataset(args.input, args.ward, args.category)
    print(f"Loaded {len(rows)} non-null rows; {len(null_rows)} null row(s) flagged above.")

    results = compute_growth(rows, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", f"{args.growth_type}_growth", "formula"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "period": r["period"],
                "ward": args.ward,
                "category": args.category,
                "actual_spend": r["actual_spend"],
                f"{args.growth_type}_growth": r["growth"],
                "formula": r["formula"],
            })

    print(f"\nGrowth output written to: {args.output}")

    # Print a quick preview
    print(f"\n{'Period':<12} {'Actual Spend':>14} {'Growth':>12}  Formula")
    print("-" * 75)
    for r in results:
        print(f"{r['period']:<12} {str(r['actual_spend']):>14} {r['growth']:>12}  {r['formula']}")


if __name__ == "__main__":
    main()

