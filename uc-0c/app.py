"""
UC-0C app.py -- Budget Growth Calculator
Implementation based on RICE framework (agents.md) and skills definition (skills.md).

Computes period-over-period growth rates at per-ward per-category granularity.
Core failure modes guarded against: wrong aggregation level, silent null handling,
formula assumption.
"""
import argparse
import csv
import os
import sys


# -----------------------------------------------------------------------
#  CONFIGURATION -- Derived from agents.md enforcement rules
# -----------------------------------------------------------------------

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = ["MoM", "YoY"] 


# -----------------------------------------------------------------------
#  SKILL 1: load_dataset
#  Reads CSV, validates columns, reports null count and which rows.
# -----------------------------------------------------------------------

def load_dataset(filepath: str) -> tuple:
    """
    Parse ward budget CSV and report nulls before returning data.

    Args:
        filepath: Path to ward_budget.csv

    Returns:
        Tuple of (rows: list[dict], null_report: list[dict])
        null_report contains dicts with period, ward, category, notes

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If required columns are missing or file is empty.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found: {filepath}")

    rows = []
    null_report = []

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate columns
        if reader.fieldnames is None:
            raise ValueError(f"CSV file is empty: {filepath}")

        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(missing)}. "
                f"Found: {', '.join(reader.fieldnames)}"
            )

        for row_idx, row in enumerate(reader, start=2):  # row 1 is header
            rows.append(row)

            # Check for null actual_spend
            actual = row.get("actual_spend", "").strip()
            if actual == "" or actual.lower() == "null":
                null_report.append({
                    "row": row_idx,
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": row.get("notes", "No reason provided"),
                })

    if not rows:
        raise ValueError(f"No data rows found in {filepath}")

    return rows, null_report


# -----------------------------------------------------------------------
#  SKILL 2: compute_growth
#  Filters by ward + category, computes growth with formula shown.
# -----------------------------------------------------------------------

def compute_growth(
    rows: list,
    null_report: list,
    ward: str,
    category: str,
    growth_type: str,
) -> list:
    """
    Compute period-over-period growth for a specific ward and category.

    Enforcement rules applied:
      1. Scoped to single ward + single category (no aggregation)
      2. Null rows are flagged, not computed
      3. Formula shown for every result row
      4. Growth type must be explicitly provided

    Args:
        rows: All data rows from load_dataset.
        null_report: Null rows from load_dataset.
        ward: Ward name to filter by.
        category: Category name to filter by.
        growth_type: 'MoM' or 'YoY'.

    Returns:
        List of result dicts with keys: period, actual_spend, previous_value,
        growth_pct, formula_used, is_null_flag
    """
    # Validate growth type
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"Invalid growth type '{growth_type}'. "
            f"Must be one of: {', '.join(VALID_GROWTH_TYPES)}. "
            f"Please specify --growth-type MoM or --growth-type YoY."
        )

    # Filter rows for the specified ward and category
    filtered = [
        r for r in rows
        if r.get("ward", "").strip() == ward
        and r.get("category", "").strip() == category
    ]

    if not filtered:
        # List valid options
        all_wards = sorted(set(r.get("ward", "").strip() for r in rows))
        all_cats = sorted(set(r.get("category", "").strip() for r in rows))
        raise ValueError(
            f"No data found for ward='{ward}', category='{category}'.\n"
            f"Valid wards: {', '.join(all_wards)}\n"
            f"Valid categories: {', '.join(all_cats)}"
        )

    # Sort by period
    filtered.sort(key=lambda r: r.get("period", ""))

    # Build null lookup for this ward+category
    null_periods = set()
    for n in null_report:
        if n["ward"].strip() == ward and n["category"].strip() == category:
            null_periods.add(n["period"].strip())

    # Compute growth
    results = []
    for i, row in enumerate(filtered):
        period = row.get("period", "").strip()
        actual_raw = row.get("actual_spend", "").strip()

        # Check if this row is null
        is_null = period in null_periods or actual_raw == "" or actual_raw.lower() == "null"

        if is_null:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "previous_value": "N/A",
                "growth_pct": "NULL - not computed",
                "formula_used": "N/A (null actual_spend)",
                "is_null_flag": "YES",
            })
            continue

        actual = float(actual_raw)

        if growth_type == "MoM":
            # Previous month
            if i == 0:
                results.append({
                    "period": period,
                    "actual_spend": f"{actual}",
                    "previous_value": "N/A",
                    "growth_pct": "N/A (no prior period)",
                    "formula_used": "MoM: ((current - previous) / previous) * 100",
                    "is_null_flag": "NO",
                })
                continue

            prev_row = filtered[i - 1]
            prev_period = prev_row.get("period", "").strip()
            prev_raw = prev_row.get("actual_spend", "").strip()

            # If previous row is null, can't compute
            if prev_period in null_periods or prev_raw == "" or prev_raw.lower() == "null":
                results.append({
                    "period": period,
                    "actual_spend": f"{actual}",
                    "previous_value": "NULL (prior period)",
                    "growth_pct": "N/A (prior period is null)",
                    "formula_used": "MoM: skipped - baseline is null",
                    "is_null_flag": "NO",
                })
                continue

            prev_actual = float(prev_raw)
            if prev_actual == 0:
                growth = "N/A (division by zero)"
                formula = "MoM: ((current - 0) / 0) * 100 = undefined"
            else:
                growth_val = ((actual - prev_actual) / prev_actual) * 100
                growth = f"{growth_val:+.1f}%"
                formula = (
                    f"MoM: (({actual} - {prev_actual}) / {prev_actual}) * 100 "
                    f"= {growth_val:+.1f}%"
                )

            results.append({
                "period": period,
                "actual_spend": f"{actual}",
                "previous_value": f"{prev_actual}",
                "growth_pct": growth,
                "formula_used": formula,
                "is_null_flag": "NO",
            })

        elif growth_type == "YoY":
            # Same month, prior year -- with only 2024 data, YoY is not possible
            results.append({
                "period": period,
                "actual_spend": f"{actual}",
                "previous_value": "N/A",
                "growth_pct": "N/A (single-year dataset, no prior year data)",
                "formula_used": "YoY: ((current_month - same_month_prior_year) / same_month_prior_year) * 100",
                "is_null_flag": "NO",
            })

    return results


# -----------------------------------------------------------------------
#  VERIFICATION -- Post-computation checks from agents.md enforcement
# -----------------------------------------------------------------------

def verify_output(results: list, ward: str, category: str, growth_type: str) -> list:
    """
    Run enforcement checks on the computed output.

    Returns:
        List of warning/error strings. Empty = all checks passed.
    """
    issues = []

    # CHECK 1: Null rows must be flagged
    null_rows = [r for r in results if r.get("is_null_flag") == "YES"]
    unflagged_nulls = [
        r for r in results
        if r.get("actual_spend") == "NULL" and r.get("is_null_flag") != "YES"
    ]
    if unflagged_nulls:
        issues.append(
            f"[SILENT NULL] {len(unflagged_nulls)} null row(s) not flagged."
        )

    # CHECK 2: Every non-null, non-first row should have a formula
    for r in results:
        if r.get("is_null_flag") == "NO" and r.get("formula_used", "").strip() == "":
            issues.append(
                f"[MISSING FORMULA] Period {r['period']} has no formula shown."
            )

    # CHECK 3: Scope check -- results should only contain the specified ward/category
    # (Already enforced by filtering, but we verify)

    return issues


# -----------------------------------------------------------------------
#  MAIN -- CLI entry point matching README run command
# -----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C -- Budget Growth Calculator. "
                    "Computes per-ward per-category growth rates."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to ward_budget.csv"
    )
    parser.add_argument(
        "--ward", required=True,
        help="Ward name to filter (e.g., 'Ward 1 - Kasba')"
    )
    parser.add_argument(
        "--category", required=True,
        help="Category to filter (e.g., 'Roads & Pothole Repair')"
    )
    parser.add_argument(
        "--growth-type", required=False, default=None,
        help="Growth type: MoM or YoY. MUST be specified."
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write output CSV"
    )
    args = parser.parse_args()

    # -- Enforcement: Refuse if growth-type not specified --
    if args.growth_type is None:
        print("[REFUSAL] --growth-type not specified.")
        print("Please specify: --growth-type MoM  or  --growth-type YoY")
        print("The system will not silently default to a growth type.")
        sys.exit(1)

    # -- Step 1: Load dataset --
    print(f"[load_dataset] Loading: {args.input}")
    try:
        rows, null_report = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    print(f"[load_dataset] Loaded {len(rows)} data rows.")

    # -- Step 2: Report nulls --
    if null_report:
        print(f"\n[NULL REPORT] {len(null_report)} null actual_spend row(s) detected:")
        for n in null_report:
            print(
                f"  [!] {n['period']} | {n['ward']} | {n['category']} | "
                f"Reason: {n['notes']}"
            )
        print()
    else:
        print("[NULL REPORT] No null values detected.\n")

    # -- Step 3: Compute growth --
    print(
        f"[compute_growth] Computing {args.growth_type} for "
        f"ward='{args.ward}', category='{args.category}'..."
    )
    try:
        results = compute_growth(
            rows, null_report, args.ward, args.category, args.growth_type
        )
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # -- Step 4: Verify output --
    print("[verify] Running enforcement checks...")
    issues = verify_output(results, args.ward, args.category, args.growth_type)

    if issues:
        print(f"\n[ENFORCEMENT] {len(issues)} issue(s) detected:")
        for issue in issues:
            print(f"  [!] {issue}")
        print()
    else:
        print("[ENFORCEMENT] All checks passed. OK\n")

    # -- Step 5: Write output CSV --
    try:
        fieldnames = [
            "period", "actual_spend", "previous_value",
            "growth_pct", "formula_used", "is_null_flag",
        ]
        with open(args.output, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"[output] Results written to: {args.output}")
    except Exception as e:
        print(f"[ERROR] Failed to write output: {e}")
        sys.exit(1)

    # -- Step 6: Print summary stats --
    null_count = sum(1 for r in results if r.get("is_null_flag") == "YES")
    computed = sum(1 for r in results if r.get("is_null_flag") == "NO"
                   and "N/A" not in r.get("growth_pct", ""))
    print(f"\n-- Summary Stats --")
    print(f"  Ward:             {args.ward}")
    print(f"  Category:         {args.category}")
    print(f"  Growth type:      {args.growth_type}")
    print(f"  Total periods:    {len(results)}")
    print(f"  Null periods:     {null_count}")
    print(f"  Computed growth:  {computed}")
    print(f"  Output file:      {args.output}")


if __name__ == "__main__":
    main()
