"""
UC-0C — Number That Looks Right
Computes MoM or YoY growth for a specified ward and category
from the municipal ward budget CSV.

Run:
    python app.py \
        --input ../data/budget/ward_budget.csv \
        --ward "Ward 1 – Kasba" \
        --category "Roads & Pothole Repair" \
        --growth-type MoM \
        --output growth_output.csv
"""

import argparse
import csv
import sys


REQUIRED_COLUMNS = {"period", "ward", "category", "actual_spend", "notes"}


def load_dataset(filepath):
    try:
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except OSError as e:
        sys.exit(f"ERROR: Cannot read '{filepath}': {e}")

    if not rows:
        sys.exit(f"ERROR: No data found in '{filepath}'.")

    missing = REQUIRED_COLUMNS - set(rows[0].keys())
    if missing:
        sys.exit(f"ERROR: Missing columns in dataset: {', '.join(sorted(missing))}")

    null_rows = [r for r in rows if r["actual_spend"].strip() == ""]
    print(f"NULL REPORT — {len(null_rows)} null actual_spend row(s) found:")
    if null_rows:
        for r in null_rows:
            print(f"  [{r['period']}] {r['ward']} | {r['category']} — {r['notes'].strip() or 'No reason given'}")
    else:
        print("  None.")
    print()

    return rows


def compute_growth(rows, ward, category, growth_type, output_path):
    subset = [
        r for r in rows
        if r["ward"].strip() == ward and r["category"].strip() == category
    ]

    if not subset:
        available_wards = sorted({r["ward"].strip() for r in rows})
        available_cats = sorted({r["category"].strip() for r in rows})
        sys.exit(
            f"ERROR: No data found for ward='{ward}' category='{category}'.\n"
            f"Available wards: {available_wards}\n"
            f"Available categories: {available_cats}"
        )

    subset = sorted(subset, key=lambda r: r["period"])

    results = []
    for i, row in enumerate(subset):
        period = row["period"]
        raw = row["actual_spend"].strip()
        current = float(raw) if raw != "" else None

        if growth_type == "MoM":
            if i == 0:
                prev = None
                formula = "N/A — first period"
            else:
                prev_raw = subset[i - 1]["actual_spend"].strip()
                prev = float(prev_raw) if prev_raw != "" else None
                formula = f"({period} {current} - prev {prev}) / prev {prev} * 100" if (current is not None and prev is not None) else "NULL_FLAGGED"
        elif growth_type == "YoY":
            year = int(period[:4])
            month = period[5:]
            prev_period = f"{year - 1}-{month}"
            prev_rows = [r for r in subset if r["period"] == prev_period]
            if not prev_rows:
                prev = None
                formula = f"N/A — no prior year period {prev_period}"
            else:
                prev_raw = prev_rows[0]["actual_spend"].strip()
                prev = float(prev_raw) if prev_raw != "" else None
                formula = f"({period} {current} - {prev_period} {prev}) / {prev_period} {prev} * 100" if (current is not None and prev is not None) else "NULL_FLAGGED"

        if current is None or (growth_type == "MoM" and i > 0 and prev is None):
            growth_pct = "NULL_FLAGGED"
            null_flag = "NULL"
            formula = "NULL_FLAGGED"
        elif formula == "N/A — first period" or formula.startswith("N/A — no prior"):
            growth_pct = "N/A"
            null_flag = ""
        else:
            growth_pct = f"{((current - prev) / prev * 100):+.1f}%"
            null_flag = ""

        results.append({
            "period":      period,
            "ward":        ward,
            "category":    category,
            "actual_spend": raw if raw != "" else "NULL",
            "growth_pct":  growth_pct,
            "formula":     formula,
            "null_flag":   null_flag,
        })

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "null_flag"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except OSError as e:
        sys.exit(f"ERROR: Cannot write to '{output_path}': {e}")

    print(f"Growth table written to: {output_path}")
    print(f"Rows: {len(results)} | NULL_FLAGGED: {sum(1 for r in results if r['null_flag'] == 'NULL')}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C: Ward budget growth analysis.")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=False, default=None, help="Exact ward name")
    parser.add_argument("--category",    required=False, default=None, help="Exact category name")
    parser.add_argument("--growth-type", required=False, default=None, dest="growth_type", help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path for output CSV")
    args = parser.parse_args()

    if not args.ward or not args.category:
        sys.exit("ERROR: Both --ward and --category must be specified. Aggregation across wards or categories is not permitted.")

    if not args.growth_type:
        sys.exit("ERROR: --growth-type must be specified. Accepted values: MoM, YoY.")

    if args.growth_type not in ("MoM", "YoY"):
        sys.exit(f"ERROR: Unknown growth type '{args.growth_type}'. Accepted values: MoM, YoY.")

    rows = load_dataset(args.input)
    compute_growth(rows, args.ward, args.category, args.growth_type, args.output)


if __name__ == "__main__":
    main()
