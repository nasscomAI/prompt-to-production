"""
UC-0C — Number That Looks Right
Computes per-ward per-category growth metrics from municipal budget data.
Enforcement: no cross-ward aggregation, null flagging before compute, formula shown, growth-type required.
"""
import argparse
import csv
import sys


def load_dataset(file_path: str) -> tuple:
    """
    Read budget CSV, validate columns, report nulls before returning data.
    Returns: (rows, null_report)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Validate required columns
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    if rows:
        actual_cols = list(rows[0].keys())
        missing = [c for c in required_cols if c not in actual_cols]
        if missing:
            print(f"ERROR: Missing required columns: {missing}", file=sys.stderr)
            sys.exit(1)

    # Identify and report null actual_spend rows
    null_report = []
    for row in rows:
        spend = row.get("actual_spend", "").strip()
        if spend == "" or spend is None:
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row.get("notes", "No reason provided")
            })

    # Print null report
    print(f"\n{'='*60}")
    print(f"DATASET LOADED: {len(rows)} rows")
    print(f"NULL ACTUAL_SPEND ROWS FOUND: {len(null_report)}")
    print(f"{'='*60}")
    if null_report:
        for nr in null_report:
            print(f"  NULL: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
    else:
        print("  WARNING: Expected 5 null rows but found 0. Check data integrity.")
    print(f"{'='*60}\n")

    return rows, null_report


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute growth for a specific ward + category combination.
    Returns list of result dicts with formula shown.
    """
    # Validate growth_type
    if growth_type not in ("MoM", "YoY"):
        print(f"ERROR: Invalid growth-type '{growth_type}'. Must be 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)

    # Filter data for specified ward and category
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]

    if not filtered:
        # List valid options
        valid_wards = sorted(set(r["ward"] for r in data))
        valid_cats = sorted(set(r["category"] for r in data))
        print(f"ERROR: No data found for ward='{ward}', category='{category}'.", file=sys.stderr)
        print(f"Valid wards: {valid_wards}", file=sys.stderr)
        print(f"Valid categories: {valid_cats}", file=sys.stderr)
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []

    for i, row in enumerate(filtered):
        period = row["period"]
        spend_raw = row["actual_spend"].strip() if row["actual_spend"] else ""

        # Check if current period is null
        if spend_raw == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_type": growth_type,
                "formula": "N/A",
                "growth_pct": "N/A",
                "flag": f"NULL — not computed. Reason: {row.get('notes', 'unknown')}"
            })
            continue

        current_spend = float(spend_raw)

        if growth_type == "MoM":
            if i == 0:
                # First period — no previous to compare
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": spend_raw,
                    "growth_type": growth_type,
                    "formula": "N/A (first period)",
                    "growth_pct": "N/A",
                    "flag": "First period — no previous data"
                })
                continue

            # Check previous period
            prev_row = filtered[i - 1]
            prev_spend_raw = prev_row["actual_spend"].strip() if prev_row["actual_spend"] else ""

            if prev_spend_raw == "":
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": spend_raw,
                    "growth_type": growth_type,
                    "formula": "N/A",
                    "growth_pct": "N/A",
                    "flag": "Previous period NULL — growth not computable"
                })
                continue

            prev_spend = float(prev_spend_raw)
            if prev_spend == 0:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": spend_raw,
                    "growth_type": growth_type,
                    "formula": f"({current_spend} - 0) / 0 * 100",
                    "growth_pct": "N/A",
                    "flag": "Division by zero — previous spend is 0"
                })
                continue

            growth = ((current_spend - prev_spend) / prev_spend) * 100
            formula = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": spend_raw,
                "growth_type": growth_type,
                "formula": formula,
                "growth_pct": f"{growth:.1f}%",
                "flag": ""
            })

        elif growth_type == "YoY":
            # Find same month in previous year
            try:
                year, month = period.split("-")
                prev_year_period = f"{int(year)-1}-{month}"
            except ValueError:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": spend_raw,
                    "growth_type": growth_type,
                    "formula": "N/A",
                    "growth_pct": "N/A",
                    "flag": "Invalid period format"
                })
                continue

            # Look for previous year data
            prev_year_rows = [r for r in filtered if r["period"] == prev_year_period]
            if not prev_year_rows:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": spend_raw,
                    "growth_type": growth_type,
                    "formula": "N/A (no prior year data)",
                    "growth_pct": "N/A",
                    "flag": "No data for same month in previous year"
                })
                continue

            prev_spend_raw = prev_year_rows[0]["actual_spend"].strip() if prev_year_rows[0]["actual_spend"] else ""
            if prev_spend_raw == "":
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": spend_raw,
                    "growth_type": growth_type,
                    "formula": "N/A",
                    "growth_pct": "N/A",
                    "flag": "Previous year period NULL — growth not computable"
                })
                continue

            prev_spend = float(prev_spend_raw)
            if prev_spend == 0:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": spend_raw,
                    "growth_type": growth_type,
                    "formula": f"({current_spend} - 0) / 0 * 100",
                    "growth_pct": "N/A",
                    "flag": "Division by zero — previous year spend is 0"
                })
                continue

            growth = ((current_spend - prev_spend) / prev_spend) * 100
            formula = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": spend_raw,
                "growth_type": growth_type,
                "formula": formula,
                "growth_pct": f"{growth:.1f}%",
                "flag": ""
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    # Step 1: Load and validate dataset, report nulls
    data, null_report = load_dataset(args.input)

    # Step 2: Compute growth
    print(f"Computing {args.growth_type} growth for: {args.ward} | {args.category}")
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    # Step 3: Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_type", "formula", "growth_pct", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults written to: {args.output}")
    print(f"Total periods: {len(results)}")
    flagged = [r for r in results if r["flag"]]
    if flagged:
        print(f"Flagged periods: {len(flagged)}")
        for f_row in flagged:
            print(f"  {f_row['period']}: {f_row['flag']}")


if __name__ == "__main__":
    main()
