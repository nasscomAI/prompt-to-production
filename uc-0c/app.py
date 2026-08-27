"""
UC-0C app.py — Budget Growth Computation Agent
Implements the load_dataset and compute_growth skills as defined in skills.md.
Follows enforcement rules from agents.md.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import math
import sys


# ─────────────────────────────────────────────────────────
# Skill: load_dataset
# ─────────────────────────────────────────────────────────

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str) -> tuple[list[dict], list[dict]]:
    """
    Reads a CSV budget file, validates columns, and reports null actual_spend
    rows before returning the data.

    Returns:
        (rows, null_report)
        - rows: list of dicts with all CSV columns
        - null_report: list of dicts with period, ward, category, reason
    """
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            # Strip BOM and whitespace from fieldnames
            reader.fieldnames = [name.strip() for name in reader.fieldnames]

            # Validate columns
            actual_columns = set(reader.fieldnames)
            missing = REQUIRED_COLUMNS - actual_columns
            if missing:
                print(f"ERROR: Missing required columns: {sorted(missing)}. "
                      f"Expected: {sorted(REQUIRED_COLUMNS)}.")
                sys.exit(1)

            rows = []
            for row in reader:
                # Strip whitespace from all values
                cleaned = {k.strip(): v.strip() if v else "" for k, v in row.items()}
                rows.append(cleaned)

    except FileNotFoundError:
        print(f"ERROR: File not found at {file_path}.")
        sys.exit(1)

    if not rows:
        print("ERROR: CSV file is empty — no data rows found.")
        sys.exit(1)

    # Detect null actual_spend rows
    null_report = []
    for row in rows:
        if row["actual_spend"] == "":
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row["notes"] if row["notes"] else "No reason provided",
            })

    # Print null report before returning
    print(f"  Loaded {len(rows)} rows.")
    if null_report:
        print(f"\n  ⚠️  {len(null_report)} null actual_spend row(s) detected:")
        for nr in null_report:
            print(f"    - {nr['period']} · {nr['ward']} · {nr['category']}")
            print(f"      Reason: {nr['reason']}")
    else:
        print("  ✅ No null actual_spend rows found.")

    return rows, null_report


# ─────────────────────────────────────────────────────────
# Skill: compute_growth
# ─────────────────────────────────────────────────────────

def compute_growth(
    rows: list[dict],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict]:
    """
    Computes per-period spending growth for a specific ward + category.

    Returns a list of dicts, one per period:
        period, actual_spend, prev_spend, formula, growth_pct, flag
    """
    # Validate ward exists
    available_wards = sorted(set(r["ward"] for r in rows))
    if ward not in available_wards:
        print(f"ERROR: Ward '{ward}' not found. "
              f"Available wards: {available_wards}")
        sys.exit(1)

    # Validate category exists
    available_categories = sorted(set(r["category"] for r in rows))
    if category not in available_categories:
        print(f"ERROR: Category '{category}' not found. "
              f"Available categories: {available_categories}")
        sys.exit(1)

    # Filter to specific ward + category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        print(f"ERROR: No data found for ward '{ward}' + category '{category}'.")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    if growth_type == "MoM":
        return _compute_mom(filtered)
    elif growth_type == "YoY":
        return _compute_yoy(filtered)
    else:
        print(f"ERROR: Unknown growth type '{growth_type}'. Use MoM or YoY.")
        sys.exit(1)


def _compute_mom(filtered: list[dict]) -> list[dict]:
    """Month-over-month growth computation."""
    results = []
    last_valid_spend = None
    last_valid_period = None

    for i, row in enumerate(filtered):
        period = row["period"]
        raw_spend = row["actual_spend"]
        notes = row["notes"]

        # NULL row — flag it, don't compute
        if raw_spend == "":
            results.append({
                "period": period,
                "actual_spend": "",
                "prev_spend": "",
                "formula": "",
                "growth_pct": "",
                "flag": f"[NULL — {notes if notes else 'No reason provided'}]",
            })
            continue

        actual = round(float(raw_spend), 1)

        # First valid row — no prior period
        if last_valid_spend is None:
            results.append({
                "period": period,
                "actual_spend": actual,
                "prev_spend": "",
                "formula": "",
                "growth_pct": "",
                "flag": "[N/A — no prior period]",
            })
            last_valid_spend = actual
            last_valid_period = period
            continue

        # Normal computation
        prev = last_valid_spend
        growth = round((actual - prev) / prev * 100, 1)
        formula = f"({actual} - {prev}) / {prev} × 100 = {growth}%"

        results.append({
            "period": period,
            "actual_spend": actual,
            "prev_spend": prev,
            "formula": formula,
            "growth_pct": growth,
            "flag": "",
        })

        last_valid_spend = actual
        last_valid_period = period

    return results


def _compute_yoy(filtered: list[dict]) -> list[dict]:
    """Year-over-year growth computation."""
    # Build a lookup: period -> actual_spend
    spend_by_period = {}
    for row in filtered:
        if row["actual_spend"] != "":
            spend_by_period[row["period"]] = round(float(row["actual_spend"]), 1)

    results = []
    for row in filtered:
        period = row["period"]
        raw_spend = row["actual_spend"]
        notes = row["notes"]

        # NULL row
        if raw_spend == "":
            results.append({
                "period": period,
                "actual_spend": "",
                "prev_spend": "",
                "formula": "",
                "growth_pct": "",
                "flag": f"[NULL — {notes if notes else 'No reason provided'}]",
            })
            continue

        actual = round(float(raw_spend), 1)

        # Find same month in prior year
        try:
            year, month = period.split("-")
            prior_period = f"{int(year) - 1}-{month}"
        except ValueError:
            prior_period = None

        if prior_period and prior_period in spend_by_period:
            prev = spend_by_period[prior_period]
            growth = round((actual - prev) / prev * 100, 1)
            formula = f"({actual} - {prev}) / {prev} × 100 = {growth}%"
            results.append({
                "period": period,
                "actual_spend": actual,
                "prev_spend": prev,
                "formula": formula,
                "growth_pct": growth,
                "flag": "",
            })
        else:
            results.append({
                "period": period,
                "actual_spend": actual,
                "prev_spend": "",
                "formula": "",
                "growth_pct": "",
                "flag": "[N/A — no prior year data]",
            })

    return results


# ─────────────────────────────────────────────────────────
# Output
# ─────────────────────────────────────────────────────────

def write_output(results: list[dict], output_path: str, ward: str, category: str, growth_type: str):
    """Write results to CSV and print summary to stdout."""
    fieldnames = ["period", "actual_spend", "prev_spend", "formula", "growth_pct", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print human-readable summary
    print(f"\n{'=' * 70}")
    print(f"  Growth Report: {ward} · {category} · {growth_type}")
    print(f"{'=' * 70}")
    print(f"  {'Period':<10} {'Actual':>8} {'Prev':>8} {'Growth':>8}  Flag")
    print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8}  {'-'*30}")

    for r in results:
        actual_str = f"{r['actual_spend']}" if r["actual_spend"] != "" else "—"
        prev_str = f"{r['prev_spend']}" if r["prev_spend"] != "" else "—"
        growth_str = f"{r['growth_pct']}%" if r["growth_pct"] != "" else "—"
        flag_str = r["flag"] if r["flag"] else ""
        print(f"  {r['period']:<10} {actual_str:>8} {prev_str:>8} {growth_str:>8}  {flag_str}")

    if any(r["formula"] for r in results):
        print(f"\n  Formulas:")
        for r in results:
            if r["formula"]:
                print(f"    {r['period']}: {r['formula']}")


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget Growth Computation Agent"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the ward_budget.csv file"
    )
    parser.add_argument(
        "--ward", required=True,
        help="Specific ward to compute growth for (required — no cross-ward aggregation)"
    )
    parser.add_argument(
        "--category", required=True,
        help="Specific category to compute growth for (required — no cross-category aggregation)"
    )
    parser.add_argument(
        "--growth-type", required=True, choices=["MoM", "YoY"],
        help="Growth type: MoM (month-over-month) or YoY (year-over-year). Required — will not guess."
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write the output CSV"
    )
    args = parser.parse_args()

    # Step 1: Load and validate dataset
    print(f"Reading dataset from: {args.input}")
    rows, null_report = load_dataset(args.input)

    # Step 2: Compute growth
    print(f"\nComputing {args.growth_type} growth for: {args.ward} · {args.category}")
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Step 3: Write output
    write_output(results, args.output, args.ward, args.category, args.growth_type)
    print(f"\n✅ Output written to {args.output}")


if __name__ == "__main__":
    main()
