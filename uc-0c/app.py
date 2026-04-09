"""
UC-0C — Number That Looks Right
Computes per-ward per-category growth rates with null flagging and formula transparency.
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import sys


def load_dataset(input_path: str) -> list:
    """
    Read ward budget CSV, validate columns, report nulls.
    Returns: list of row dicts.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Validate required columns
    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    if not required.issubset(set(rows[0].keys())):
        missing = required - set(rows[0].keys())
        raise ValueError(f"Missing columns: {missing}")

    # Report null actual_spend rows
    nulls = [r for r in rows if not r["actual_spend"] or r["actual_spend"].strip() == ""]
    print(f"\n  Dataset loaded: {len(rows)} rows")
    print(f"  Null actual_spend rows: {len(nulls)}")
    if nulls:
        print("  ┌─ NULL REPORT ──────────────────────────────────────────")
        for r in nulls:
            reason = r.get("notes", "No reason provided").strip()
            print(f"  │ {r['period']} | {r['ward']} | {r['category']}")
            print(f"  │   Reason: {reason}")
        print("  └───────────────────────────────────────────────────────")

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str,
                   output_path: str):
    """
    Compute per-period growth for a specific ward + category.
    Writes output CSV with formula shown.
    """
    # Validate growth type
    if growth_type not in ("MoM",):
        if growth_type == "YoY":
            print("\n  ✗ REFUSED: YoY growth cannot be computed — dataset contains")
            print("    only one year (2024). Use --growth-type MoM instead.")
            sys.exit(1)
        else:
            print(f"\n  ✗ REFUSED: Unknown growth type '{growth_type}'.")
            print("    Supported: MoM (Month-over-Month)")
            sys.exit(1)

    # Validate ward exists
    valid_wards = sorted(set(r["ward"] for r in rows))
    if ward not in valid_wards:
        print(f"\n  ✗ REFUSED: Ward '{ward}' not found.")
        print(f"    Valid wards: {valid_wards}")
        sys.exit(1)

    # Validate category exists
    valid_cats = sorted(set(r["category"] for r in rows))
    if category not in valid_cats:
        print(f"\n  ✗ REFUSED: Category '{category}' not found.")
        print(f"    Valid categories: {valid_cats}")
        sys.exit(1)

    # Filter to specified ward + category, sort by period
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        print(f"\n  ✗ No data for {ward} / {category}")
        sys.exit(1)

    # Compute MoM growth
    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_raw = row["actual_spend"].strip() if row["actual_spend"] else ""
        notes = row.get("notes", "").strip()

        # Check for null
        if not actual_raw:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "previous_spend": "",
                "growth_rate_pct": "N/A",
                "formula": "Cannot compute — actual_spend is NULL",
                "flag": f"NULL: {notes}" if notes else "NULL: reason not provided",
            })
            continue

        actual = float(actual_raw)

        if i == 0:
            results.append({
                "period": period,
                "actual_spend": f"{actual}",
                "previous_spend": "",
                "growth_rate_pct": "N/A",
                "formula": "First period — no previous data",
                "flag": "",
            })
            continue

        # Check if previous period was null
        prev_raw = filtered[i - 1]["actual_spend"].strip() if filtered[i - 1]["actual_spend"] else ""
        if not prev_raw:
            results.append({
                "period": period,
                "actual_spend": f"{actual}",
                "previous_spend": "NULL",
                "growth_rate_pct": "N/A",
                "formula": "Cannot compute — previous period actual_spend is NULL",
                "flag": "Previous period NULL",
            })
            continue

        prev = float(prev_raw)
        if prev == 0:
            growth = "N/A"
            formula = f"({actual} - {prev}) / {prev} — division by zero"
            flag = "Previous spend is zero"
        else:
            growth_val = ((actual - prev) / prev) * 100
            growth = f"{growth_val:+.1f}%"
            formula = f"({actual} - {prev}) / {prev} x 100 = {growth}"
            flag = ""

        results.append({
            "period": period,
            "actual_spend": f"{actual}",
            "previous_spend": f"{prev}",
            "growth_rate_pct": growth,
            "formula": formula,
            "flag": flag,
        })

    # Write output
    fieldnames = ["period", "actual_spend", "previous_spend",
                  "growth_rate_pct", "formula", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n  ✓ Growth table written to {output_path}")
    print(f"    Ward: {ward}")
    print(f"    Category: {category}")
    print(f"    Growth type: {growth_type}")
    print(f"    Periods: {len(results)}")

    # Print summary table
    print(f"\n  {'Period':<10} {'Actual':>8} {'Prev':>8} {'Growth':>10}  Flag")
    print(f"  {'─'*10} {'─'*8} {'─'*8} {'─'*10}  {'─'*20}")
    for r in results:
        actual = r['actual_spend']
        prev = r['previous_spend'] if r['previous_spend'] else "—"
        growth = r['growth_rate_pct']
        flag = r['flag'] if r['flag'] else ""
        print(f"  {r['period']:<10} {actual:>8} {prev:>8} {growth:>10}  {flag}")


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget Growth Calculator (per-ward per-category only)"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True,
                        help="Growth calculation type: MoM (Month-over-Month)")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    compute_growth(rows, args.ward, args.category, args.growth_type, args.output)
    print("\nDone.")


if __name__ == "__main__":
    main()
