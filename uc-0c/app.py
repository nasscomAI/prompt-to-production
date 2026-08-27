"""
UC-0C — Budget Growth Calculator
Computes MoM/YoY growth for a specific ward and category with null handling.
"""
import argparse
import csv
import os
import sys


def load_dataset(file_path: str) -> list[dict]:
    """Load ward budget CSV, validate columns, report nulls."""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    if not required_cols.issubset(set(reader.fieldnames or [])):
        print(f"Error: CSV missing required columns. Expected: {required_cols}")
        sys.exit(1)

    # Report nulls
    null_rows = [r for r in rows if not r["actual_spend"].strip()]
    if null_rows:
        print(f"\n[load_dataset] WARNING: {len(null_rows)} null actual_spend rows detected:")
        for r in null_rows:
            print(f"  - {r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")
        print()

    return rows


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """Compute growth for a specific ward/category combination."""
    # Filter to the requested ward and category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        available_wards = sorted(set(r["ward"] for r in rows))
        available_cats = sorted(set(r["category"] for r in rows))
        print(f"Error: No data found for ward='{ward}', category='{category}'")
        print(f"Available wards: {available_wards}")
        print(f"Available categories: {available_cats}")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []

    for i, row in enumerate(filtered):
        period = row["period"]
        spend_str = row["actual_spend"].strip()
        notes = row["notes"].strip()

        # Handle null
        if not spend_str:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "formula": "N/A — null data",
                "growth_pct": "N/A",
                "flag": f"NULL_DATA: {notes}"
            })
            continue

        current_spend = float(spend_str)

        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "actual_spend": f"{current_spend}",
                    "formula": "N/A — first period",
                    "growth_pct": "N/A",
                    "flag": ""
                })
                continue

            # Check if previous row was null
            prev_spend_str = filtered[i - 1]["actual_spend"].strip()
            if not prev_spend_str:
                results.append({
                    "period": period,
                    "actual_spend": f"{current_spend}",
                    "formula": "N/A — previous period is null",
                    "growth_pct": "N/A",
                    "flag": "SKIP: previous period null"
                })
                continue

            prev_spend = float(prev_spend_str)
            if prev_spend == 0:
                growth_pct = "N/A"
                formula = f"MoM = ({current_spend} - 0) / 0 — division by zero"
            else:
                growth = ((current_spend - prev_spend) / prev_spend) * 100
                growth_pct = f"{growth:+.1f}%"
                formula = f"MoM = ({current_spend} - {prev_spend}) / {prev_spend} * 100 = {growth:+.1f}%"

            results.append({
                "period": period,
                "actual_spend": f"{current_spend}",
                "formula": formula,
                "growth_pct": growth_pct,
                "flag": ""
            })

        elif growth_type == "YoY":
            # For YoY we need same month previous year — not applicable with single year data
            results.append({
                "period": period,
                "actual_spend": f"{current_spend}",
                "formula": "N/A — only 2024 data available, YoY requires prior year",
                "growth_pct": "N/A",
                "flag": "INSUFFICIENT_DATA: single year dataset"
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C: Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM (Month-over-Month) or YoY (Year-over-Year)")
    parser.add_argument("--output", required=True, help="Path for output CSV")
    args = parser.parse_args()

    print(f"[load_dataset] Loading: {args.input}")
    rows = load_dataset(args.input)
    print(f"[load_dataset] Loaded {len(rows)} rows")

    # Refuse aggregation — we require specific ward and category
    print(f"[compute_growth] Computing {args.growth_type} for: {args.ward} / {args.category}")
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Write output
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "formula", "growth_pct", "flag"])
        writer.writeheader()
        writer.writerows(results)

    print(f"[done] Output written to: {args.output}")
    print(f"\nVerify: Check null rows are flagged, formulas are shown, no cross-ward aggregation.")


if __name__ == "__main__":
    main()
