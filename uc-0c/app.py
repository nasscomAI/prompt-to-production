"""
UC-0C — Number That Looks Right

Computes month-over-month (MoM) or year-over-year (YoY) growth rates for
municipal budget actual spending, at per-ward per-category granularity only.
Flags null rows, shows formulas, and refuses cross-ward aggregation.

Usage:
    python app.py --input ../data/budget/ward_budget.csv \
                  --ward "Ward 1 – Kasba" \
                  --category "Roads & Pothole Repair" \
                  --growth-type MoM \
                  --output growth_output.csv
"""
import argparse
import csv
import sys


def load_dataset(file_path: str) -> tuple:
    """
    Read ward budget CSV, validate columns, report nulls.
    Returns (rows, null_report).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("ERROR: Dataset is empty.", file=sys.stderr)
        sys.exit(1)

    # Validate columns
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    actual_cols = set(rows[0].keys())
    missing = [c for c in required_cols if c not in actual_cols]
    if missing:
        print(f"ERROR: Missing columns: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    # Identify null actual_spend rows
    null_report = []
    for row in rows:
        if not row["actual_spend"].strip():
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row.get("notes", "No reason provided")
            })

    # Print null report
    print(f"Dataset loaded: {len(rows)} rows.")
    print(f"\nNULL ACTUAL_SPEND REPORT ({len(null_report)} rows):")
    print("-" * 60)
    if null_report:
        for nr in null_report:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']}")
            print(f"    Reason: {nr['notes']}")
    else:
        print("  No null rows found.")
    print("-" * 60)
    print()

    return rows, null_report


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute growth for a specific ward + category.
    Returns list of result dicts.
    """
    # Validate growth_type
    valid_types = ["MoM", "YoY"]
    if growth_type not in valid_types:
        print(f"ERROR: Invalid growth-type '{growth_type}'. Must be one of: {', '.join(valid_types)}", file=sys.stderr)
        sys.exit(1)

    # Filter data
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        available_wards = sorted(set(r["ward"] for r in rows))
        available_cats = sorted(set(r["category"] for r in rows))
        print(f"ERROR: No data found for ward='{ward}', category='{category}'", file=sys.stderr)
        print(f"  Available wards: {available_wards}", file=sys.stderr)
        print(f"  Available categories: {available_cats}", file=sys.stderr)
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Compute growth
    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_str = row["actual_spend"].strip()
        notes = row.get("notes", "")

        # Handle null current value
        if not actual_str:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "previous_spend": "",
                "growth_pct": "NULL - not computed",
                "formula": "N/A",
                "flag": f"NULL - not computed. Reason: {notes}"
            })
            continue

        actual = float(actual_str)

        # Determine previous period index
        if growth_type == "MoM":
            prev_idx = i - 1
        else:  # YoY
            prev_idx = i - 12

        # First period or no previous available
        if prev_idx < 0:
            results.append({
                "period": period,
                "actual_spend": f"{actual:.1f}",
                "previous_spend": "N/A",
                "growth_pct": "N/A (no previous period)",
                "formula": f"MoM = (current - previous) / previous * 100",
                "flag": ""
            })
            continue

        # Check if previous period has null
        prev_row = filtered[prev_idx]
        prev_str = prev_row["actual_spend"].strip()

        if not prev_str:
            prev_notes = prev_row.get("notes", "")
            results.append({
                "period": period,
                "actual_spend": f"{actual:.1f}",
                "previous_spend": "NULL",
                "growth_pct": "NULL - not computed",
                "formula": "N/A",
                "flag": f"NULL - previous period ({prev_row['period']}) has null actual_spend. Reason: {prev_notes}"
            })
            continue

        # Compute growth
        previous = float(prev_str)
        if previous == 0:
            growth_pct = "INF (division by zero)"
            formula = f"MoM = ({actual:.1f} - 0.0) / 0.0 * 100 = undefined"
        else:
            growth = (actual - previous) / previous * 100
            growth_pct = f"{growth:+.1f}%"
            formula = f"MoM = ({actual:.1f} - {previous:.1f}) / {previous:.1f} * 100 = {growth:+.1f}%"

        results.append({
            "period": period,
            "actual_spend": f"{actual:.1f}",
            "previous_spend": f"{previous:.1f}",
            "growth_pct": growth_pct,
            "formula": formula,
            "flag": ""
        })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator — per-ward per-category growth rates"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category name to filter")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth calculation type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    # Refuse aggregation attempts
    if args.ward.lower() in ["all", "total", "combined", "*"]:
        print("REFUSED: Cross-ward aggregation is not supported.", file=sys.stderr)
        print("  This tool computes growth for a single ward + category only.", file=sys.stderr)
        print("  Please specify a specific ward name.", file=sys.stderr)
        sys.exit(1)

    if args.category.lower() in ["all", "total", "combined", "*"]:
        print("REFUSED: Cross-category aggregation is not supported.", file=sys.stderr)
        print("  This tool computes growth for a single ward + category only.", file=sys.stderr)
        print("  Please specify a specific category name.", file=sys.stderr)
        sys.exit(1)

    # Step 1: Load and report
    rows, null_report = load_dataset(args.input)

    # Step 2: Compute
    print(f"Computing {args.growth_type} growth for: {args.ward} | {args.category}")
    print()
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Step 3: Write output
    output_fields = ["period", "actual_spend", "previous_spend", "growth_pct", "formula", "flag"]
    try:
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Could not write output: {e}", file=sys.stderr)
        sys.exit(2)

    # Step 4: Summary
    total = len(results)
    computed = sum(1 for r in results if r["growth_pct"] not in ["N/A (no previous period)", "NULL - not computed"])
    nulls = sum(1 for r in results if "NULL" in r["growth_pct"])
    print(f"Results written to {args.output}")
    print(f"  Periods: {total}")
    print(f"  Computed: {computed}")
    print(f"  Null/skipped: {nulls}")


if __name__ == "__main__":
    main()
