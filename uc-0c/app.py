"""
UC-0C -- Number That Looks Right
Built using agents.md (RICE framework) and skills.md enforcement rules.

Implements two skills:
  - load_dataset   : reads CSV, validates columns, reports ALL nulls before returning
  - compute_growth : per-ward per-category growth table with formula shown on every row

Enforcement rules from agents.md:
  1. Never aggregate across wards/categories -- refuse if no ward/category specified
  2. Flag every null actual_spend row BEFORE computing -- include in output as NULL
  3. Show formula used on every output row alongside the result
  4. If --growth-type not specified -- refuse, never guess
  5. Output must be per-period table, not a single number
  6. Validate all required columns present before proceeding

Reference values (README):
  Ward 1 Kasba | Roads & Pothole Repair | 2024-07 | 19.7 | +33.1% (monsoon spike)
  Ward 1 Kasba | Roads & Pothole Repair | 2024-10 | 13.1 | -34.8% (post-monsoon)
  Ward 2 Shivajinagar | Drainage & Flooding | 2024-03 | NULL  | must be flagged
  Ward 4 Warje | Roads & Pothole Repair  | 2024-07 | NULL  | must be flagged
"""
import argparse
import csv
import os
import sys


# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

VALID_GROWTH_TYPES = {"MoM", "YoY"}

# Known null rows from README (for verification in null report)
KNOWN_NULLS = [
    ("2024-03", "Ward 2 - Shivajinagar", "Drainage & Flooding"),
    ("2024-07", "Ward 4 - Warje",        "Roads & Pothole Repair"),
    ("2024-11", "Ward 1 - Kasba",        "Waste Management"),
    ("2024-08", "Ward 3 - Kothrud",      "Parks & Greening"),
    ("2024-05", "Ward 5 - Hadapsar",     "Streetlight Maintenance"),
]


# -------------------------------------------------------------------------
# Skill 1: load_dataset
# -------------------------------------------------------------------------

def load_dataset(file_path: str) -> tuple[list[dict], list[dict]]:
    """
    Read and validate the ward_budget CSV. Report ALL null rows BEFORE returning.

    Input:  file_path (str) -- path to ward_budget.csv
    Output: (data, null_report)
              data        -- list of row dicts with actual_spend as float or None
              null_report -- list of null row dicts (period, ward, category, notes)

    Error handling:
      - File not found / unreadable     -> clear error + exit
      - Any required column missing     -> refuse with named missing columns + exit
      - Empty CSV                       -> warning + exit
      - Row parse failure               -> include in null_report, mark parse error
    """
    # --- Validate file exists ---
    if not os.path.isfile(file_path):
        print(f"ERROR: Input file not found: {file_path}")
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = set(reader.fieldnames or [])

            # --- Validate required columns ---
            missing_cols = REQUIRED_COLUMNS - fieldnames
            if missing_cols:
                print(f"ERROR: Required column(s) missing from CSV: {sorted(missing_cols)}")
                print("       Cannot proceed with partial data.")
                sys.exit(1)

            rows = list(reader)
    except Exception as e:
        print(f"ERROR: Failed to read CSV '{file_path}': {e}")
        sys.exit(1)

    if not rows:
        print(f"WARNING: CSV file has no data rows: {file_path}")
        sys.exit(1)

    # --- Parse rows, flag nulls ---
    data = []
    null_report = []

    for i, row in enumerate(rows, start=2):  # 2 = first data row (1=header)
        try:
            actual_raw = row.get("actual_spend", "").strip()
            if actual_raw == "" or actual_raw.lower() == "null":
                actual_spend = None
                null_report.append({
                    "period":   row["period"].strip(),
                    "ward":     row["ward"].strip(),
                    "category": row["category"].strip(),
                    "notes":    row.get("notes", "").strip() or "(no note provided)",
                })
            else:
                actual_spend = float(actual_raw)

            budgeted = row.get("budgeted_amount", "").strip()
            data.append({
                "period":           row["period"].strip(),
                "ward":             row["ward"].strip(),
                "category":         row["category"].strip(),
                "budgeted_amount":  float(budgeted) if budgeted else None,
                "actual_spend":     actual_spend,
                "notes":            row.get("notes", "").strip(),
            })

        except Exception as e:
            # Row parse failure -- include in null_report, keep in data as None
            null_report.append({
                "period":   row.get("period", f"row_{i}"),
                "ward":     row.get("ward", "unknown"),
                "category": row.get("category", "unknown"),
                "notes":    f"parse error: {e}",
            })
            data.append({
                "period":           row.get("period", f"row_{i}"),
                "ward":             row.get("ward", "unknown"),
                "category":         row.get("category", "unknown"),
                "budgeted_amount":  None,
                "actual_spend":     None,
                "notes":            f"parse error: {e}",
            })

    # --- Print null report BEFORE any computation (agents.md enforcement rule 2) ---
    print("=" * 70)
    print("NULL SPEND REPORT (flagged BEFORE computation)")
    print("=" * 70)
    if null_report:
        print(f"  {len(null_report)} null actual_spend row(s) found:\n")
        for nr in null_report:
            print(f"  [NULL] {nr['period']} | {nr['ward']} | {nr['category']}")
            print(f"         Reason: {nr['notes']}")
    else:
        print("  No null rows found.")
    print("=" * 70)
    print(f"\n  Dataset loaded: {len(data)} rows total, {len(null_report)} null(s)\n")

    return data, null_report


# -------------------------------------------------------------------------
# Skill 2: compute_growth
# -------------------------------------------------------------------------

def compute_growth(data: list[dict], ward: str, category: str,
                   growth_type: str) -> list[dict]:
    """
    Compute per-period growth for a specific ward and category.

    Input:
      data        -- full dataset from load_dataset
      ward        -- exact ward name (must match dataset)
      category    -- exact category name (must match dataset)
      growth_type -- "MoM" or "YoY" only -- NEVER defaulted (agents.md rule 4)

    Output:
      List of per-period dicts with: period, ward, category, actual_spend,
      previous_spend, growth_rate, formula_used, notes.
      Null rows are INCLUDED and marked -- never dropped (agents.md rule 2).

    Error handling:
      - Invalid growth_type -> refuse with clear error, exit
      - Ward/category not found -> refuse with clear error, exit
      - Null previous/current -> mark row as NULL not computed, continue
      - First period with no prior -> mark NULL not computed
    """
    # --- Enforcement: refuse if growth_type invalid (agents.md rule 4) ---
    if growth_type not in VALID_GROWTH_TYPES:
        print(f"ERROR: --growth-type must be MoM or YoY.")
        print(f"       Got: '{growth_type}'")
        print(f"       Choosing a formula without user instruction is not permitted.")
        sys.exit(1)

    # --- Filter to requested ward + category ---
    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]

    # --- Refuse if no matching rows found (agents.md rule 6) ---
    if not filtered:
        print(f"ERROR: No data found for ward='{ward}' category='{category}'.")
        print(f"       Check spelling and exact capitalisation.")
        print(f"       Available wards/categories can be found in the input CSV.")
        sys.exit(1)

    # --- Sort by period ---
    filtered.sort(key=lambda r: r["period"])

    # --- Build period-indexed lookup for previous period lookup ---
    period_to_spend = {row["period"]: row["actual_spend"] for row in filtered}
    all_periods = sorted(period_to_spend.keys())

    results = []

    for i, row in enumerate(filtered):
        period       = row["period"]
        actual_spend = row["actual_spend"]
        notes        = row["notes"]

        # --- Determine previous spend based on growth_type ---
        previous_spend = None
        prev_label     = ""

        if growth_type == "MoM":
            if i == 0:
                prev_label = "no prior period available (first period in dataset)"
            else:
                prev_period    = all_periods[i - 1]
                previous_spend = period_to_spend.get(prev_period)
                prev_label     = prev_period

        elif growth_type == "YoY":
            # Same month of prior year
            year, month    = period.split("-")
            prior_period   = f"{int(year) - 1}-{month}"
            previous_spend = period_to_spend.get(prior_period)
            prev_label     = prior_period if prior_period in period_to_spend \
                             else f"{prior_period} (not in dataset)"

        # --- Compute growth rate ---
        if actual_spend is None:
            growth_rate  = f"NULL -- not computed: actual_spend is null for {period}"
            formula_used = "N/A -- current period value is null"

        elif previous_spend is None:
            if i == 0 and growth_type == "MoM":
                growth_rate  = "NULL -- not computed: no prior period available"
            else:
                growth_rate  = f"NULL -- not computed: previous period ({prev_label}) value is null"
            formula_used = f"N/A -- previous value ({prev_label}) is null"

        else:
            try:
                rate = (actual_spend - previous_spend) / previous_spend * 100
                sign = "+" if rate >= 0 else ""
                growth_rate  = f"{sign}{rate:.1f}%"
                formula_used = (
                    f"({actual_spend} - {previous_spend}) / {previous_spend} * 100"
                    f" = {sign}{rate:.1f}%"
                )
            except ZeroDivisionError:
                growth_rate  = "NULL -- not computed: previous_spend is zero (division by zero)"
                formula_used = f"({actual_spend} - {previous_spend}) / {previous_spend} * 100 -- ERROR: division by zero"

        results.append({
            "period":          period,
            "ward":            ward,
            "category":        category,
            "actual_spend":    actual_spend if actual_spend is not None else "NULL",
            "previous_spend":  previous_spend if previous_spend is not None else "NULL",
            "growth_rate":     growth_rate,
            "formula_used":    formula_used,
            "notes":           notes,
        })

    return results


# -------------------------------------------------------------------------
# CLI entry point
# -------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Analysis -- Per-Ward Per-Category Growth Calculator"
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name to analyse")
    parser.add_argument("--category",    required=True,  help="Exact category name to analyse")
    parser.add_argument("--growth-type", required=False, dest="growth_type",
                        help="MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # --- Enforcement: refuse if --growth-type not given (agents.md rule 4) ---
    if not args.growth_type:
        print("ERROR: --growth-type is required. Specify MoM or YoY.")
        print("       Choosing a formula without user instruction is not permitted.")
        sys.exit(1)

    print()
    print("UC-0C Budget Growth Analyser")
    print(f"  Input       : {args.input}")
    print(f"  Ward        : {args.ward}")
    print(f"  Category    : {args.category}")
    print(f"  Growth type : {args.growth_type}")
    print(f"  Output      : {args.output}")
    print()

    # Skill 1: load_dataset (nulls reported before computation)
    print("Step 1: Loading and validating dataset...")
    data, null_report = load_dataset(args.input)

    # Skill 2: compute_growth
    print(f"Step 2: Computing {args.growth_type} growth for "
          f"'{args.ward}' / '{args.category}'...")
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    # --- Write output CSV ---
    output_fields = [
        "period", "ward", "category", "actual_spend",
        "previous_spend", "growth_rate", "formula_used", "notes"
    ]
    try:
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Failed to write output '{args.output}': {e}")
        sys.exit(1)

    # --- Print results table to terminal ---
    print()
    print("=" * 70)
    print(f"  {args.growth_type} GROWTH RESULTS -- {args.ward} / {args.category}")
    print("=" * 70)
    print(f"  {'Period':<10} {'Actual':>10} {'Previous':>10} {'Growth':>12}  Formula")
    print(f"  {'-'*10} {'-'*10} {'-'*10} {'-'*12}  {'-'*30}")
    for r in results:
        actual   = str(r["actual_spend"])
        previous = str(r["previous_spend"])
        growth   = r["growth_rate"]
        formula  = r["formula_used"][:55]  # truncate for display
        print(f"  {r['period']:<10} {actual:>10} {previous:>10} {growth:>12}  {formula}")
    print("=" * 70)

    # --- Summary ---
    null_result_rows = sum(1 for r in results if "NULL" in str(r["growth_rate"]))
    computed_rows    = len(results) - null_result_rows
    print(f"\n  Summary:")
    print(f"    Periods analysed : {len(results)}")
    print(f"    Growth computed  : {computed_rows}")
    print(f"    NULL (not computed): {null_result_rows}")
    print(f"    Output written to: {args.output}")
    print()
    print("Done.")


if __name__ == "__main__":
    main()
