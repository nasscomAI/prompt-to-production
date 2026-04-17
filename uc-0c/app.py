"""
UC-0C — Number That Looks Right
Implements the load_dataset and compute_growth skills defined in skills.md,
enforcing every rule from agents.md.

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
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("uc-0c")


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    """
    Reads the budget CSV, validates columns, reports nulls.
    Returns (rows, null_report) where:
      - rows: list of all parsed rows
      - null_report: list of dicts for rows where actual_spend is blank/null
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []

            # Validate required columns
            missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
            if missing:
                logger.error(
                    f"Missing required columns: {missing}. "
                    f"Found: {fieldnames}"
                )
                sys.exit(1)

            rows = list(reader)
    except Exception as exc:
        logger.error(f"Failed to read input file {input_path}: {exc}")
        sys.exit(1)

    # Check for critical nulls in key columns
    for idx, row in enumerate(rows, start=1):
        for col in ["period", "ward", "category"]:
            if not row.get(col, "").strip():
                logger.error(
                    f"Data quality issue: row {idx} has empty '{col}'. "
                    f"Cannot proceed with malformed data."
                )
                sys.exit(1)

    # Build null report for actual_spend
    null_report: list[dict] = []
    valid_count = 0
    for row in rows:
        spend = row.get("actual_spend", "").strip()
        if not spend:
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row.get("notes", "").strip() or "No reason provided",
            })
        else:
            valid_count += 1

    # Report nulls before any computation
    print(f"\n{'='*60}")
    print(f"  DATASET LOADED: {input_path}")
    print(f"{'='*60}")
    print(f"  Total rows:  {len(rows)}")
    print(f"  Valid rows:  {valid_count}")
    print(f"  Null rows:   {len(null_report)}")

    if null_report:
        print(f"\n  [!] NULL actual_spend rows (excluded from computation):")
        print(f"  {'-'*56}")
        for nr in null_report:
            print(f"  * {nr['period']} | {nr['ward']} | "
                  f"{nr['category']} - {nr['reason']}")
    print(f"{'='*60}\n")

    return rows, null_report


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(
    rows: list[dict],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict]:
    """
    Computes per-period growth for a specific ward + category.

    Enforcement (agents.md):
      • Never aggregate across wards/categories.
      • Flag null rows — exclude from computation.
      • Show formula in every output row.
      • Refuse if growth_type not specified.
    """
    # Filter rows for the specific ward + category
    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]

    if not filtered:
        # List valid values to help the user
        valid_wards = sorted(set(r["ward"] for r in rows))
        valid_cats = sorted(set(r["category"] for r in rows))
        logger.error(
            f"No data found for ward='{ward}', category='{category}'.\n"
            f"  Valid wards: {valid_wards}\n"
            f"  Valid categories: {valid_cats}"
        )
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Build output table
    results: list[dict] = []

    for i, row in enumerate(filtered):
        period = row["period"]
        spend_raw = row.get("actual_spend", "").strip()

        # Current value
        if not spend_raw:
            current_spend = None
            flag = "NULL_PERIOD"
        else:
            current_spend = float(spend_raw)
            flag = ""

        # Previous period value (for MoM: previous month; for YoY: same month last year)
        prev_spend = None
        prev_period = ""

        if growth_type == "MoM":
            if i > 0:
                prev_row = filtered[i - 1]
                prev_period = prev_row["period"]
                prev_raw = prev_row.get("actual_spend", "").strip()
                if prev_raw:
                    prev_spend = float(prev_raw)
                else:
                    flag = flag or "NULL_PRIOR"
            else:
                prev_period = "N/A (first period)"

        elif growth_type == "YoY":
            # Find same month in previous year
            try:
                year, month = period.split("-")
                target = f"{int(year) - 1}-{month}"
                for r in filtered:
                    if r["period"] == target:
                        prev_period = target
                        prev_raw = r.get("actual_spend", "").strip()
                        if prev_raw:
                            prev_spend = float(prev_raw)
                        else:
                            flag = flag or "NULL_PRIOR"
                        break
                if not prev_period:
                    prev_period = f"N/A ({target} not in dataset)"
            except ValueError:
                prev_period = "N/A (invalid period format)"

        # Compute growth rate
        if current_spend is not None and prev_spend is not None and prev_spend != 0:
            growth_rate = ((current_spend - prev_spend) / prev_spend) * 100
            formula = (
                f"({current_spend} - {prev_spend}) / {prev_spend} × 100 "
                f"= {growth_rate:+.1f}%"
            )
            growth_str = f"{growth_rate:+.1f}%"
        elif current_spend is None:
            formula = "N/A — current period actual_spend is null"
            growth_str = "N/A"
            flag = "NULL_PERIOD"
        elif prev_spend is None and i > 0 and prev_period and "first" not in prev_period and "not in" not in prev_period:
            formula = "N/A — prior period actual_spend is null"
            growth_str = "N/A"
            flag = flag or "NULL_PRIOR"
        else:
            formula = "N/A — no prior period available"
            growth_str = "N/A"

        results.append({
            "period": period,
            "actual_spend": spend_raw if spend_raw else "NULL",
            "previous_period": prev_period,
            "previous_period_spend": str(prev_spend) if prev_spend is not None else "NULL",
            "formula": formula,
            "growth_rate": growth_str,
            "flag": flag,
        })

    return results


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True,
                        help="Exact ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True,
                        help="Exact category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, default=None,
                        help="Growth type: MoM or YoY (REQUIRED)")
    parser.add_argument("--output", required=True,
                        help="Path to write growth output CSV")
    args = parser.parse_args()

    # Enforcement: refuse if growth-type not specified
    if not args.growth_type:
        print("ERROR: --growth-type is required. Please specify MoM or YoY.")
        print("  MoM = Month-over-Month growth")
        print("  YoY = Year-over-Year growth")
        print("  The system will NOT default to a growth type silently.")
        sys.exit(1)

    if args.growth_type not in ("MoM", "YoY"):
        print(f"ERROR: Invalid growth type '{args.growth_type}'. "
              f"Must be exactly 'MoM' or 'YoY'.")
        sys.exit(1)

    # Skill 1: load_dataset — reports nulls before computation
    rows, null_report = load_dataset(args.input)

    # Skill 2: compute_growth — per-ward, per-category, with formula
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Write output CSV
    if not results:
        logger.warning("No results to write.")
        return

    fieldnames = list(results[0].keys())
    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as exc:
        logger.error(f"Failed to write output file {args.output}: {exc}")
        sys.exit(1)

    # Print results table to console
    print(f"Growth Report: {args.ward} | {args.category} | {args.growth_type}")
    print(f"{'-'*80}")
    print(f"{'Period':<10} {'Spend':>8} {'Prev':>8} {'Growth':>10} {'Flag':<12} Formula")
    print(f"{'-'*80}")
    for r in results:
        print(
            f"{r['period']:<10} "
            f"{r['actual_spend']:>8} "
            f"{r['previous_period_spend']:>8} "
            f"{r['growth_rate']:>10} "
            f"{r['flag']:<12} "
            f"{r['formula']}"
        )
    print(f"{'-'*80}")
    print(f"\nDone. Results written to {args.output}")


if __name__ == "__main__":
    main()
