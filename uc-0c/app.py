# -*- coding: utf-8 -*-
"""
UC-0C  --  Number That Looks Right
Per-ward, per-category budget growth calculator.

Enforcement (from agents.md):
  1. Never aggregate across wards or categories -- refuse if asked.
  2. Flag every null row before computing -- report null reason from notes.
  3. Show formula used in every output row alongside the result.
  4. If --growth-type not specified -- refuse and ask, never guess.
"""

import sys
import os
import argparse
import csv

# ---------------------------------------------------------------------------
# Reconfigure stdout / stderr for UTF-8 on Windows so em-dashes print safely
# ---------------------------------------------------------------------------
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = [
    "period", "ward", "category",
    "budgeted_amount", "actual_spend", "notes",
]


# ===================================================================
# SKILL 1 : load_dataset
# ===================================================================
def load_dataset(file_path):
    """
    Reads the ward budget CSV using only the csv stdlib module.
    Validates columns, reports every null actual_spend row with its
    notes reason, and returns (rows, header, null_rows).
    """

    # -- Error: file does not exist --
    if not os.path.isfile(file_path):
        print(f"[ERROR] File not found: '{file_path}'")
        sys.exit(1)

    # -- Read CSV --
    try:
        with open(file_path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            header = reader.fieldnames
            rows = list(reader)
    except Exception as exc:
        print(f"[ERROR] Cannot read '{file_path}': {exc}")
        sys.exit(1)

    # -- Error: missing columns --
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        print("[ERROR] Missing required columns:")
        for c in missing:
            print(f"  - {c}")
        sys.exit(1)

    # -- Error: empty dataset --
    if len(rows) == 0:
        print(f"[ERROR] Dataset '{file_path}' has zero rows.")
        sys.exit(1)

    # -- Identify null actual_spend rows --
    null_rows = []
    for r in rows:
        val = r["actual_spend"].strip() if r["actual_spend"] else ""
        if val == "":
            null_rows.append(r)

    # -- Report --
    print()
    print("=" * 64)
    print(f"[DATASET LOADED] {len(rows)} rows from '{file_path}'")
    print(f"[NULL REPORT]    {len(null_rows)} row(s) with missing actual_spend")

    if null_rows:
        print()
        print("  Rows with NULL actual_spend (FLAGGED -- will not be computed):")
        print()
        for r in null_rows:
            reason = r.get("notes", "").strip() or "No reason provided"
            print(f"  [NULL] {r['period']}  |  {r['ward']}  |  {r['category']}")
            print(f"         Reason: {reason}")
            print()

    print("=" * 64)

    return rows, null_rows


# ===================================================================
# SKILL 2 : compute_growth
# ===================================================================
def compute_growth(all_rows, ward, category, growth_type):
    """
    Filters to a single ward + category, then computes per-period
    growth.  Returns a list-of-dicts ready to write as CSV.

    Enforcement checks are applied here as a second layer of defence
    (first layer is in main).
    """

    # -- Refuse if growth_type missing --
    if not growth_type:
        print("[REFUSED] --growth-type was not provided.")
        print("  Please specify:  --growth-type MoM   or   --growth-type YoY")
        print("  This agent never guesses the formula.")
        sys.exit(1)

    gt = growth_type.strip().upper()
    if gt not in ("MOM", "YOY"):
        print(f"[REFUSED] '{growth_type}' is not valid.")
        print("  Allowed values:  MoM  (Month-over-Month)  |  YoY  (Year-over-Year)")
        sys.exit(1)

    # -- Refuse aggregation keywords --
    for label, value in [("ward", ward), ("category", category)]:
        if value.strip().lower() in ("all", "*", "any", ""):
            print(f"[REFUSED] Cannot aggregate across all {label} values.")
            print("  This agent computes per-ward, per-category growth only.")
            print("  Please specify a single ward AND a single category.")
            sys.exit(1)

    # -- Validate ward against data --
    known_wards = sorted(set(r["ward"] for r in all_rows))
    if ward not in known_wards:
        print(f"[REFUSED] Ward '{ward}' not found in dataset.")
        print("  Valid wards:")
        for w in known_wards:
            print(f"    - {w}")
        sys.exit(1)

    # -- Validate category against data --
    known_cats = sorted(set(r["category"] for r in all_rows))
    if category not in known_cats:
        print(f"[REFUSED] Category '{category}' not found in dataset.")
        print("  Valid categories:")
        for c in known_cats:
            print(f"    - {c}")
        sys.exit(1)

    # -- Filter & sort --
    subset = [
        r for r in all_rows
        if r["ward"] == ward and r["category"] == category
    ]
    subset.sort(key=lambda r: r["period"])

    if not subset:
        print(f"[ERROR] No rows for ward='{ward}', category='{category}'.")
        sys.exit(1)

    # -- Flag nulls in this subset before computing --
    null_here = [r for r in subset if (r["actual_spend"].strip() if r["actual_spend"] else "") == ""]
    if null_here:
        print()
        print("[NULL FLAG] Null actual_spend in this ward/category:")
        for r in null_here:
            reason = r.get("notes", "").strip() or "No reason provided"
            print(f"  [NULL] {r['period']} -- {reason}")
        print()

    # -- Helper to parse float safely --
    def to_float(val):
        v = val.strip() if val else ""
        if v == "":
            return None
        return float(v)

    # -- Build results --
    results = []
    formula_template_mom = "MoM% = ((spend[t] - spend[t-1]) / spend[t-1]) x 100"
    formula_template_yoy = "YoY% = ((spend[t] - spend[t-12]) / spend[t-12]) x 100"

    if gt == "MOM":
        prev_actual = None
        prev_period = None

        for r in subset:
            period = r["period"]
            actual = to_float(r["actual_spend"])

            if actual is None:
                reason = r.get("notes", "").strip() or ""
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "NULL",
                    "growth_value": "",
                    "formula": formula_template_mom,
                    "null_flag": "TRUE -- not computed",
                    "null_reason": reason,
                })
                # Do NOT update prev_actual -- null row is skipped for chaining
                continue

            if prev_actual is None:
                growth_str = "N/A -- no prior period"
                formula_used = formula_template_mom
            else:
                growth_val = ((actual - prev_actual) / prev_actual) * 100
                growth_str = f"{growth_val:+.1f}%"
                formula_used = (
                    f"MoM% = (({actual} - {prev_actual}) / {prev_actual}) x 100"
                    f"  [{period} vs {prev_period}]"
                )

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual),
                "growth_value": growth_str,
                "formula": formula_used,
                "null_flag": "",
                "null_reason": "",
            })

            prev_actual = actual
            prev_period = period

    elif gt == "YOY":
        # Build a {period: actual} map
        period_map = {}
        for r in subset:
            val = to_float(r["actual_spend"])
            period_map[r["period"]] = val

        for r in subset:
            period = r["period"]
            actual = to_float(r["actual_spend"])

            if actual is None:
                reason = r.get("notes", "").strip() or ""
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "NULL",
                    "growth_value": "",
                    "formula": formula_template_yoy,
                    "null_flag": "TRUE -- not computed",
                    "null_reason": reason,
                })
                continue

            # Prior year same month
            try:
                yr, mn = int(period[:4]), int(period[5:7])
                prior_period = f"{yr - 1}-{mn:02d}"
            except Exception:
                prior_period = None

            if prior_period and prior_period in period_map:
                prior_actual = period_map[prior_period]
                if prior_actual is None:
                    growth_str = "N/A -- prior year period is NULL"
                    formula_used = formula_template_yoy
                else:
                    growth_val = ((actual - prior_actual) / prior_actual) * 100
                    growth_str = f"{growth_val:+.1f}%"
                    formula_used = (
                        f"YoY% = (({actual} - {prior_actual}) / {prior_actual}) x 100"
                        f"  [{period} vs {prior_period}]"
                    )
            else:
                growth_str = "N/A -- no prior year period in dataset"
                formula_used = formula_template_yoy

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual),
                "growth_value": growth_str,
                "formula": formula_used,
                "null_flag": "",
                "null_reason": "",
            })

    return results


# ===================================================================
# CLI
# ===================================================================
def parse_args():
    p = argparse.ArgumentParser(
        description="UC-0C: Per-ward, per-category budget growth calculator."
    )
    p.add_argument("--input",    required=True, help="Path to ward_budget.csv")
    p.add_argument("--ward",     required=True, help="Exact ward name (quoted)")
    p.add_argument("--category", required=True, help="Exact category name (quoted)")
    p.add_argument(
        "--growth-type", dest="growth_type", default=None,
        help="MoM or YoY (REQUIRED -- agent refuses if omitted)",
    )
    p.add_argument("--output",   required=True, help="Output CSV file path")
    return p.parse_args()


def main():
    args = parse_args()

    # Enforcement Rule 4 -- refuse if --growth-type not given
    if args.growth_type is None:
        print()
        print("[REFUSED] --growth-type was not provided.")
        print("  This agent never guesses the growth formula.")
        print("  Please re-run with:")
        print("    --growth-type MoM   (Month-over-Month)")
        print("    --growth-type YoY   (Year-over-Year)")
        sys.exit(1)

    # Skill 1 -- load_dataset
    all_rows, null_rows = load_dataset(args.input)

    # Skill 2 -- compute_growth
    print()
    print(f"[COMPUTING] {args.growth_type.upper()} growth for:")
    print(f"  Ward     : {args.ward}")
    print(f"  Category : {args.category}")
    print()

    results = compute_growth(all_rows, args.ward, args.category, args.growth_type)

    # Write output CSV
    fieldnames = [
        "period", "ward", "category", "actual_spend",
        "growth_value", "formula", "null_flag", "null_reason",
    ]
    with open(args.output, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Console summary
    null_flagged = sum(1 for r in results if r["null_flag"])
    computed = len(results) - null_flagged

    print("[RESULTS]")
    print()
    print(f"  {'Period':<10}  {'Actual Spend':>14}  {'Growth':>22}  Null?")
    print(f"  {'-'*10}  {'-'*14}  {'-'*22}  {'-'*5}")
    for r in results:
        spend = r["actual_spend"]
        growth = r["growth_value"] if r["growth_value"] else "--"
        flag = r["null_flag"] if r["null_flag"] else ""
        print(f"  {r['period']:<10}  {spend:>14}  {growth:>22}  {flag}")

    print()
    print(f"[OUTPUT] Written to '{args.output}'")
    print(f"         Total rows: {len(results)}  |  Null-flagged: {null_flagged}  |  Computed: {computed}")


if __name__ == "__main__":
    main()
