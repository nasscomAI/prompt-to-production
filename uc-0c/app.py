"""
UC-0C app.py — Municipal budget growth analysis.
Reads ward budget CSV, filters to a single ward+category, computes MoM or YoY growth,
and writes a per-period table with actual_spend, growth, formula, and null flags.
"""
import argparse
import csv
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Compute ward budget growth (MoM or YoY).")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category name to filter")
    parser.add_argument("--growth-type", required=False, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    return parser.parse_args()


def load_dataset(filepath):
    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required_columns.issubset(set(reader.fieldnames or [])):
            missing = required_columns - set(reader.fieldnames or [])
            raise ValueError(f"Missing required columns: {missing}")
        rows = list(reader)
    null_rows = []
    for row in rows:
        if row["actual_spend"] == "" or row["actual_spend"] is None:
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row["notes"],
            })
    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]
    if not filtered:
        raise ValueError(f"No rows found for ward={ward!r}, category={category!r}")

    filtered.sort(key=lambda r: r["period"])

    def period_key(p):
        parts = p.split("-")
        return int(parts[0]), int(parts[1])

    period_map = {r["period"]: r for r in filtered}
    periods = sorted(period_map.keys(), key=period_key)

    if growth_type == "MoM":
        formula = "(current - previous) / previous * 100"
    elif growth_type == "YoY":
        formula = "(current - same_month_last_year) / same_month_last_year * 100"
    else:
        raise ValueError(f"Invalid growth-type: {growth_type!r}. Must be MoM or YoY.")

    output_rows = []
    for i, period in enumerate(periods):
        row = period_map[period]
        actual_spend_raw = row["actual_spend"]
        is_null = actual_spend_raw == "" or actual_spend_raw is None

        if is_null:
            output_rows.append({
                "period": period,
                "actual_spend": "",
                "growth": "",
                "formula": formula,
                "null_flag": "NULL",
                "reason": row["notes"],
            })
            continue

        actual_spend = float(actual_spend_raw)
        growth_value = None

        if growth_type == "MoM":
            if i == 0:
                growth_value = None
            else:
                prev_period = periods[i - 1]
                prev_row = period_map[prev_period]
                prev_raw = prev_row["actual_spend"]
                if prev_raw == "" or prev_raw is None:
                    growth_value = None
                else:
                    prev_val = float(prev_raw)
                    if prev_val == 0:
                        growth_value = None
                    else:
                        growth_value = (actual_spend - prev_val) / prev_val * 100
        elif growth_type == "YoY":
            y, m = period.split("-")
            prev_period = f"{int(y) - 1}-{m}"
            if prev_period not in period_map:
                growth_value = None
            else:
                prev_row = period_map[prev_period]
                prev_raw = prev_row["actual_spend"]
                if prev_raw == "" or prev_raw is None:
                    growth_value = None
                else:
                    prev_val = float(prev_raw)
                    if prev_val == 0:
                        growth_value = None
                    else:
                        growth_value = (actual_spend - prev_val) / prev_val * 100

        if growth_value is None:
            output_rows.append({
                "period": period,
                "actual_spend": actual_spend_raw,
                "growth": "",
                "formula": formula,
                "null_flag": "",
                "reason": "",
            })
        else:
            output_rows.append({
                "period": period,
                "actual_spend": actual_spend_raw,
                "growth": f"{growth_value:+.1f}%",
                "formula": formula,
                "null_flag": "",
                "reason": "",
            })

    return output_rows


def main():
    args = parse_args()

    if not args.growth_type:
        print("Error: --growth-type is required. Please specify MoM or YoY.", file=sys.stderr)
        sys.exit(1)

    if args.growth_type not in ("MoM", "YoY"):
        print(f"Error: --growth-type must be MoM or YoY, got {args.growth_type!r}.", file=sys.stderr)
        sys.exit(1)

    rows, null_rows = load_dataset(args.input)
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "actual_spend", "growth", "formula", "null_flag", "reason"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for orow in output_rows:
            writer.writerow(orow)


if __name__ == "__main__":
    main()