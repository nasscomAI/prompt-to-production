"""
UC-0C — Number That Looks Right
App implementation enforcing per-ward per-category scope, null row flagging,
and growth formula transparency.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path: str, ward: str = None, category: str = None):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not ward or not category:
        print("ERROR: Refused. Un-scoped aggregation across all wards/categories is not permitted.")
        print("Please specify both --ward and --category explicitly.")
        sys.exit(1)

    rows = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip():
                rows.append(r)

    if not rows:
        print(f"ERROR: No matching data found for ward '{ward}' and category '{category}'.")
        sys.exit(1)

    # Sort rows by period
    rows.sort(key=lambda x: x["period"])
    return rows


def compute_growth(rows: list, growth_type: str):
    if not growth_type:
        print("ERROR: Refused. --growth-type not specified. Please specify --growth-type (e.g. MoM).")
        sys.exit(1)

    if growth_type.upper() != "MOM":
        print(f"ERROR: Refused. Growth type '{growth_type}' not supported. Only 'MoM' is supported.")
        sys.exit(1)

    output_rows = []
    prev_actual = None

    for r in rows:
        period = r["period"]
        ward = r["ward"]
        category = r["category"]
        budgeted = r["budgeted_amount"]
        raw_actual = r["actual_spend"].strip()
        notes = r.get("notes", "").strip()

        if not raw_actual:
            # Null actual spend
            actual_str = "NULL"
            growth_str = "FLAGGED"
            formula_str = "N/A (Data missing)"
            flag_note = f"FLAGGED: {notes}" if notes else "FLAGGED: Missing actual_spend value"
            prev_actual = None  # reset prev_actual since current month spend is missing
        else:
            actual = float(raw_actual)
            actual_str = f"{actual:.1f}"
            flag_note = notes if notes else ""

            if prev_actual is None:
                growth_str = "N/A (Baseline)"
                formula_str = "N/A (First period)"
            else:
                pct_change = ((actual - prev_actual) / prev_actual) * 100.0
                sign = "+" if pct_change > 0 else ""
                growth_str = f"{sign}{pct_change:.1f}%"
                formula_str = f"(({actual:.1f} - {prev_actual:.1f}) / {prev_actual:.1f}) * 100"

            prev_actual = actual

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual_str,
            "mom_growth_pct": growth_str,
            "formula": formula_str,
            "notes": flag_note
        })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, dest="growth_type", help="Growth calculation type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    # Scope & parameter check
    if not args.ward or not args.category or not args.growth_type:
        print("ERROR: Refused. Missing required scope flags (--ward, --category, --growth-type).")
        print("System refuses all-ward or un-scoped aggregations.")
        sys.exit(1)

    rows = load_dataset(args.input, args.ward, args.category)
    results = compute_growth(rows, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "mom_growth_pct", "formula", "notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth calculation complete. Written to {args.output}")


if __name__ == "__main__":
    main()
