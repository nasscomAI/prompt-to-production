"""
UC-0C — Number That Looks Right
Financial Data Analyst: per-ward per-category growth metrics with strict
null handling, formula transparency, and anti-aggregation enforcement.
Built using agents.md (RICE enforcement) + skills.md (load_dataset, compute_growth).
"""
import argparse
import csv
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
ALLOWED_GROWTH_TYPES = ["MoM", "YoY"]


# ═══════════════════════════════════════════════════════════════════════════
# Skill: load_dataset
# ═══════════════════════════════════════════════════════════════════════════

def load_dataset(file_path: str) -> tuple[list[dict], list[dict]]:
    """
    Reads the CSV dataset, validates columns, reports null count and
    identifies which rows have null values.

    Returns:
        (all_rows, null_rows) where null_rows are rows with blank actual_spend.

    Error handling:
        - Halts if required columns are missing
        - Halts if file format is incorrect or file not found
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Validate columns
            if reader.fieldnames is None:
                logger.error("CSV file has no headers.")
                sys.exit(1)

            missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing:
                logger.error(f"Missing required columns: {missing}")
                sys.exit(1)

            all_rows: list[dict] = []
            null_rows: list[dict] = []

            for row in reader:
                all_rows.append(row)
                spend = row.get("actual_spend", "").strip()
                if spend == "":
                    null_rows.append(row)

    except FileNotFoundError:
        logger.error(f"Dataset file not found: {file_path}")
        sys.exit(1)
    except Exception as exc:
        logger.error(f"Cannot read dataset: {exc}")
        sys.exit(1)

    # ── Report null rows before any computation (enforcement rule #2) ──
    logger.info(f"Loaded {len(all_rows)} rows from {file_path}")
    logger.info(f"Null actual_spend rows found: {len(null_rows)}")

    if null_rows:
        logger.info("=" * 60)
        logger.info("NULL ROW REPORT (flagged before computation)")
        logger.info("=" * 60)
        for nr in null_rows:
            reason = nr.get("notes", "").strip() or "No reason provided"
            logger.info(
                f"  NULL: {nr['period']} | {nr['ward']} | {nr['category']} | "
                f"Reason: {reason}"
            )
        logger.info("=" * 60)

    return all_rows, null_rows


# ═══════════════════════════════════════════════════════════════════════════
# Skill: compute_growth
# ═══════════════════════════════════════════════════════════════════════════

def compute_growth(
    all_rows: list[dict],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict]:
    """
    Computes growth metrics for a given ward and category over time.

    Returns a per-period table with: period, actual_spend, growth_pct,
    formula, flag, null_reason.

    Enforcement:
        - growth_type must be specified (MoM or YoY)
        - Null rows are skipped from computation and flagged with reason
        - Formula is shown for every output row
        - Never aggregates across wards or categories
    """
    # ── Filter to exact ward + category ────────────────────────────────
    filtered = [
        r for r in all_rows
        if r["ward"] == ward and r["category"] == category
    ]

    if not filtered:
        logger.error(f"No data found for ward='{ward}', category='{category}'")
        sys.exit(1)

    # ── Sort by period ─────────────────────────────────────────────────
    filtered.sort(key=lambda r: r["period"])

    # ── Build output rows ──────────────────────────────────────────────
    results: list[dict] = []

    for i, row in enumerate(filtered):
        period = row["period"]
        spend_str = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()
        budgeted = row.get("budgeted_amount", "").strip()

        # Handle null spend
        if spend_str == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "budgeted_amount": budgeted,
                "growth_pct": "NULL",
                "formula": "N/A — actual_spend is null",
                "flag": "NULL_VALUE",
                "null_reason": notes or "No reason provided",
            })
            continue

        actual_spend = float(spend_str)

        # Determine comparison period index
        if growth_type == "MoM":
            comp_idx = i - 1
            compare_label = "prior month"
        elif growth_type == "YoY":
            comp_idx = i - 12
            compare_label = "same month prior year"
        else:
            # Should not reach here due to earlier validation
            logger.error(f"Unsupported growth_type: {growth_type}")
            sys.exit(1)

        # Check if comparison period exists
        if comp_idx < 0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual_spend:.1f}",
                "budgeted_amount": budgeted,
                "growth_pct": "N/A",
                "formula": f"No {compare_label} available for comparison",
                "flag": "",
                "null_reason": "",
            })
            continue

        # Check if comparison period had null spend
        comp_row = filtered[comp_idx]
        comp_spend_str = comp_row.get("actual_spend", "").strip()

        if comp_spend_str == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual_spend:.1f}",
                "budgeted_amount": budgeted,
                "growth_pct": "NULL",
                "formula": f"Cannot compute — {compare_label} ({comp_row['period']}) actual_spend is null",
                "flag": "PRIOR_NULL",
                "null_reason": f"Prior period ({comp_row['period']}) null: {comp_row.get('notes', '').strip() or 'No reason'}",
            })
            continue

        comp_spend = float(comp_spend_str)

        # Compute growth
        if comp_spend == 0:
            growth_pct = "INF"
            formula_str = f"({actual_spend:.1f} - 0.0) / 0.0 = undefined (division by zero)"
            flag = "DIVISION_BY_ZERO"
        else:
            growth = ((actual_spend - comp_spend) / comp_spend) * 100
            growth_pct = f"{growth:+.1f}%"
            formula_str = (
                f"({actual_spend:.1f} - {comp_spend:.1f}) / {comp_spend:.1f} × 100 "
                f"= {growth:+.1f}%"
            )
            flag = ""

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{actual_spend:.1f}",
            "budgeted_amount": budgeted,
            "growth_pct": growth_pct,
            "formula": formula_str,
            "flag": flag,
            "null_reason": "",
        })

    return results


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Financial Data Analyst — Ward Budget Growth Calculator"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Exact category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="Growth metric type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    # ── Enforcement: refuse if --growth-type not specified ──────────────
    if args.growth_type is None:
        logger.error(
            "ERROR: --growth-type not specified. "
            "You must explicitly choose MoM (month-over-month) or YoY (year-over-year). "
            "This system will never guess the growth type."
        )
        sys.exit(1)

    if args.growth_type not in ALLOWED_GROWTH_TYPES:
        logger.error(
            f"ERROR: Invalid growth type '{args.growth_type}'. "
            f"Allowed values: {ALLOWED_GROWTH_TYPES}"
        )
        sys.exit(1)

    # ── Enforcement: refuse aggregation across wards/categories ────────
    if args.ward.lower() in ("all", "*", "any", "total", "aggregate"):
        logger.error(
            "ERROR: Aggregation across wards is NOT permitted. "
            "You must specify a single ward. This system refuses cross-ward aggregation."
        )
        sys.exit(1)

    if args.category.lower() in ("all", "*", "any", "total", "aggregate"):
        logger.error(
            "ERROR: Aggregation across categories is NOT permitted. "
            "You must specify a single category. This system refuses cross-category aggregation."
        )
        sys.exit(1)

    # ── Skill 1: load_dataset ──────────────────────────────────────────
    all_rows, null_rows = load_dataset(args.input)

    # ── Skill 2: compute_growth ────────────────────────────────────────
    logger.info(
        f"Computing {args.growth_type} growth for: "
        f"ward='{args.ward}', category='{args.category}'"
    )
    results = compute_growth(all_rows, args.ward, args.category, args.growth_type)

    # ── Write output CSV ───────────────────────────────────────────────
    output_fields = [
        "period", "ward", "category", "actual_spend", "budgeted_amount",
        "growth_pct", "formula", "flag", "null_reason",
    ]

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    # ── Print table to console ─────────────────────────────────────────
    print(f"\n{'='*90}")
    print(f"  {args.growth_type} Growth Report: {args.ward} | {args.category}")
    print(f"{'='*90}")
    print(f"  {'Period':<10} {'Spend':>8} {'Growth':>10}  {'Formula / Note'}")
    print(f"  {'-'*10} {'-'*8} {'-'*10}  {'-'*50}")

    for r in results:
        flag_mark = f" [{r['flag']}]" if r["flag"] else ""
        null_note = f" (Reason: {r['null_reason']})" if r["null_reason"] else ""
        print(
            f"  {r['period']:<10} {r['actual_spend']:>8} {r['growth_pct']:>10}  "
            f"{r['formula']}{flag_mark}{null_note}"
        )

    print(f"{'='*90}")
    print(f"\nDone. Results written to {args.output}")


if __name__ == "__main__":
    main()
