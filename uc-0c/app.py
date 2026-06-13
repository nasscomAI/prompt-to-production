"""
import io
UC-0C app.py — Budget Growth Calculation Agent
Implements the RICE + agents.md + skills.md + CRAFT workflow.

Skills used:
  - load_dataset  : reads CSV, validates columns, reports ALL null rows, filters to ward+category
  - compute_growth: computes MoM or YoY growth per period; flags nulls; shows formula used

Enforcement rules (from agents.md):
  1. Never aggregate across wards/categories — --ward and --category are mandatory
  2. Flag every null actual_spend BEFORE computing
  3. Show formula used in every output row
  4. If --growth-type is missing/invalid — refuse; never guess

Run (as specified in README):
  python app.py \\
    --input ../data/budget/ward_budget.csv \\
    --ward "Ward 1 – Kasba" \\
    --category "Roads & Pothole Repair" \\
    --growth-type MoM \\
    --output growth_output.csv
"""

import argparse
import io
import os
import sys
import csv
from pathlib import Path
from datetime import datetime

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
VALID_GROWTH_TYPES = {"MoM", "YoY"}


# ──────────────────────────────────────────────
# SKILL: load_dataset
# ──────────────────────────────────────────────
def load_dataset(file_path: str, ward: str, category: str):
    """
    Reads the ward budget CSV, validates columns, reports ALL null actual_spend rows,
    then returns the filtered dataset for the specified ward + category.

    Returns:
        (filtered_rows, null_rows, available_wards, available_categories)

    Raises:
        FileNotFoundError — if path is invalid
        ValueError        — if columns missing, or ward/category not found
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"[load_dataset] Input file not found: '{file_path}'\n"
            "Check the --input path and try again."
        )

    try:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)
            fieldnames = set(reader.fieldnames or [])
    except Exception as e:
        raise FileNotFoundError(f"[load_dataset] Cannot read file '{file_path}': {e}") from e

    # Validate columns
    missing_cols = REQUIRED_COLUMNS - fieldnames
    if missing_cols:
        raise ValueError(
            f"[load_dataset] Missing required columns: {sorted(missing_cols)}\n"
            f"Found columns: {sorted(fieldnames)}"
        )

    # Collect all nulls from the FULL dataset before filtering
    null_rows = []
    available_wards = set()
    available_categories = set()

    for row in all_rows:
        available_wards.add(row["ward"])
        available_categories.add(row["category"])
        if row["actual_spend"].strip() == "":
            null_rows.append({
                "period":   row["period"],
                "ward":     row["ward"],
                "category": row["category"],
                "reason":   row["notes"].strip() if row["notes"].strip() else "No reason provided"
            })

    # Validate ward and category exist
    if ward not in available_wards:
        raise ValueError(
            f"[load_dataset] Ward '{ward}' not found in dataset.\n"
            f"Available wards: {sorted(available_wards)}"
        )
    if category not in available_categories:
        raise ValueError(
            f"[load_dataset] Category '{category}' not found in dataset.\n"
            f"Available categories: {sorted(available_categories)}"
        )

    # Filter to the requested ward + category, sorted by period
    filtered_rows = [
        r for r in all_rows
        if r["ward"] == ward and r["category"] == category
    ]
    filtered_rows.sort(key=lambda r: r["period"])

    return filtered_rows, null_rows, sorted(available_wards), sorted(available_categories)


# ──────────────────────────────────────────────
# SKILL: compute_growth
# ──────────────────────────────────────────────
def compute_growth(filtered_rows: list, growth_type: str, null_rows: list) -> list:
    """
    Computes per-period growth rates for a filtered ward+category dataset.

    MoM: (current - previous_month) / previous_month * 100
    YoY: (current - same_month_last_year) / same_month_last_year * 100

    Returns:
        List of result dicts with keys:
        [period, ward, category, actual_spend, growth_pct, formula_used, null_flag, null_reason]

    Raises:
        ValueError — if growth_type is not "MoM" or "YoY"
    """
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"[compute_growth] Invalid growth_type '{growth_type}'.\n"
            f"Must be one of: {VALID_GROWTH_TYPES}\n"
            "Refusing to guess — please specify --growth-type explicitly."
        )

    # Build a quick lookup: period → actual_spend (or None)
    period_to_spend = {}
    for row in filtered_rows:
        raw = row["actual_spend"].strip()
        period_to_spend[row["period"]] = float(raw) if raw != "" else None

    # Build a set of null periods for quick flag lookup
    null_period_set = {
        (n["period"], n["ward"], n["category"]) for n in null_rows
    }

    results = []

    for row in filtered_rows:
        period     = row["period"]
        ward_name  = row["ward"]
        cat_name   = row["category"]
        raw_spend  = row["actual_spend"].strip()
        notes      = row["notes"].strip()

        is_null = (raw_spend == "")
        current_val = float(raw_spend) if not is_null else None

        if is_null:
            results.append({
                "period":       period,
                "ward":         ward_name,
                "category":     cat_name,
                "actual_spend": "NULL",
                "growth_pct":   "",
                "formula_used": "SKIPPED — actual_spend is NULL",
                "null_flag":    "TRUE",
                "null_reason":  notes if notes else "No reason provided"
            })
            continue

        # Determine the comparison period
        try:
            dt = datetime.strptime(period, "%Y-%m")
        except ValueError:
            results.append({
                "period":       period,
                "ward":         ward_name,
                "category":     cat_name,
                "actual_spend": f"{current_val:.1f}",
                "growth_pct":   "",
                "formula_used": "N/A — period format unrecognised",
                "null_flag":    "FALSE",
                "null_reason":  ""
            })
            continue

        if growth_type == "MoM":
            # Previous month
            if dt.month == 1:
                prev_period = f"{dt.year - 1}-12"
            else:
                prev_period = f"{dt.year}-{dt.month - 1:02d}"
        else:  # YoY
            prev_period = f"{dt.year - 1}-{dt.month:02d}"

        prev_val = period_to_spend.get(prev_period)

        if prev_val is None and prev_period not in period_to_spend:
            # Prior period not in dataset at all
            formula_str = f"N/A — no prior period ({prev_period} not in dataset)"
            growth_pct  = ""
        elif prev_val is None:
            # Prior period exists but is null
            formula_str = f"SKIPPED — prior period {prev_period} has NULL actual_spend"
            growth_pct  = ""
        else:
            growth_raw  = (current_val - prev_val) / prev_val * 100
            growth_pct  = f"{growth_raw:+.2f}%"
            formula_str = (
                f"{growth_type}: ({current_val:.1f} - {prev_val:.1f}) "
                f"/ {prev_val:.1f} * 100 = {growth_raw:+.2f}%"
            )

        results.append({
            "period":       period,
            "ward":         ward_name,
            "category":     cat_name,
            "actual_spend": f"{current_val:.1f}",
            "growth_pct":   growth_pct,
            "formula_used": formula_str,
            "null_flag":    "FALSE",
            "null_reason":  ""
        })

    return results


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Per-ward per-category budget growth calculator."
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name (exact match)")
    parser.add_argument("--category",    required=True,  help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True,  dest="growth_type",
                        help="Growth formula: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output",      required=True,  help="Output CSV file path")
    args = parser.parse_args()

    # Enforcement: validate growth_type before loading data
    if args.growth_type not in VALID_GROWTH_TYPES:
        print(
            f"\nERROR: --growth-type '{args.growth_type}' is not valid.\n"
            f"Must be one of: {sorted(VALID_GROWTH_TYPES)}\n"
            "Refusing to guess a formula — please specify explicitly.",
            file=sys.stderr
        )
        sys.exit(1)

    # ── SKILL: load_dataset ──────────────────
    print(f"\n[load_dataset] Loading: {args.input}")
    try:
        filtered_rows, null_rows, avail_wards, avail_cats = load_dataset(
            args.input, args.ward, args.category
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[load_dataset] {len(filtered_rows)} rows for ward='{args.ward}' | category='{args.category}'")

    # Enforcement: Report ALL nulls BEFORE computing
    print(f"\n[load_dataset] NULL actual_spend rows found in FULL dataset: {len(null_rows)}")
    if null_rows:
        print("  These rows will be flagged in output and excluded from growth calculation:")
        for n in null_rows:
            print(f"  [NULL] {n['period']} | {n['ward']} | {n['category']} -> \"{n['reason']}\"")
    print()

    # ── SKILL: compute_growth ────────────────
    print(f"[compute_growth] Formula: {args.growth_type}")
    try:
        results = compute_growth(filtered_rows, args.growth_type, null_rows)
    except ValueError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # ── Write output CSV ─────────────────────
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["period", "ward", "category", "actual_spend",
                  "growth_pct", "formula_used", "null_flag", "null_reason"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"[output] Written {len(results)} rows → {output_path.resolve()}")
    print(f"[done] Growth calculation complete. Formula used: {args.growth_type}. All nulls flagged.")


if __name__ == "__main__":
    main()
