"""
UC-0C — app.py  (Number That Looks Right)
==========================================
Role    : Budget Growth Analyst — per-ward, per-category only.
          Reads  : ../data/budget/ward_budget.csv
          Writes : growth_output.csv
Intent  : Produce a per-period CSV with actual_spend, growth %, formula,
          and null flags.  Reference values from README:
            2024-07 | Ward 1 – Kasba | Roads & Pothole Repair → +33.1 % MoM
            2024-10 | Ward 1 – Kasba | Roads & Pothole Repair → −34.8 % MoM
            2024-03 | Ward 2 – Shivajinagar | Drainage & Flooding → NULL (flagged)
            2024-07 | Ward 4 – Warje | Roads & Pothole Repair  → NULL (flagged)
Context : Only ../data/budget/ward_budget.csv is allowed.  No external APIs.
          No zero-fill / interpolation for null actual_spend rows.
          growth-type MUST be supplied via --growth-type (MoM or YoY).
Enforce : REFUSE aggregation | FLAG every null | SHOW formula | REFUSE if
          --growth-type missing | VALIDATE columns on load.

Skills implemented
------------------
  load_dataset   — reads CSV, validates 6 columns, reports null count +
                   which rows before returning.
  compute_growth — per-ward per-category growth table with formula shown.

Run:
  python app.py \\
    --input ../data/budget/ward_budget.csv \\
    --ward  "Ward 1 – Kasba" \\
    --category "Roads & Pothole Repair" \\
    --growth-type MoM \\
    --output growth_output.csv
"""

import argparse
import sys
import pandas as pd

# ── Constants ──────────────────────────────────────────────────────────────────
REQUIRED_COLUMNS = {"period", "ward", "category",
                    "budgeted_amount", "actual_spend", "notes"}
VALID_GROWTH_TYPES = {"MoM", "YoY"}


# ══════════════════════════════════════════════════════════════════════════════
#  SKILL 1 — load_dataset
#  Reads CSV, validates columns, reports null rows BEFORE any computation.
# ══════════════════════════════════════════════════════════════════════════════
def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Reads ward_budget.csv, validates the 6 required columns, and prints
    a null-row report.  Refuses to continue on any schema or data error.

    Returns
    -------
    pd.DataFrame  — validated, full 300-row dataset.
    """
    # ── File load ──────────────────────────────────────────────────────────────
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        sys.exit(f"[ERROR] File not found: {file_path}")

    if df.empty:
        sys.exit("[ERROR] Empty dataset — 0 rows loaded.")

    # ── Column validation (agents.md enforcement: VALIDATE) ───────────────────
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        sys.exit(f"[ERROR] Missing required column(s): {sorted(missing)}\n"
                 f"        Expected: {sorted(REQUIRED_COLUMNS)}\n"
                 f"        Found   : {sorted(df.columns.tolist())}")

    # ── Null-row report BEFORE computation (skills.md: load_dataset output) ───
    null_mask = df["actual_spend"].isna()
    null_rows = df[null_mask]

    print(f"\n[load_dataset] Loaded {len(df)} rows from: {file_path}")
    print(f"[load_dataset] Null actual_spend rows: {len(null_rows)} "
          f"(expected: 5)\n")

    if len(null_rows) > 0:
        print("[load_dataset] Flagging all NULL rows before any computation:")
        for _, row in null_rows.iterrows():
            reason = row["notes"] if pd.notna(row["notes"]) and str(row["notes"]).strip() else "No reason provided"
            print(f"  NULL → {row['period']} | {row['ward']} | "
                  f"{row['category']} | Reason: {reason}")
    print()

    return df


# ══════════════════════════════════════════════════════════════════════════════
#  SKILL 2 — compute_growth
#  Per-ward per-category growth with formula shown.  Refuses aggregation.
# ══════════════════════════════════════════════════════════════════════════════
def compute_growth(df: pd.DataFrame,
                   ward: str,
                   category: str,
                   growth_type: str,
                   output_path: str) -> None:
    """
    Filters to the requested ward + category, computes MoM or YoY growth,
    shows the arithmetic formula for every computed value, flags all null rows,
    and writes the result to growth_output.csv.

    Enforcement guards
    ------------------
    • growth_type must be "MoM" or "YoY" — never guessed.
    • Null rows are flagged; growth is NOT computed for them or adjacent periods.
    • Formula is shown for every non-null growth value.
    • Aggregation across wards / categories is refused.
    """

    # ── Guard: growth_type explicit (agents.md enforcement: REFUSE if missing) ─
    if growth_type not in VALID_GROWTH_TYPES:
        sys.exit(
            f"[REFUSE] Invalid --growth-type '{growth_type}'.\n"
            f"         Allowed values: MoM, YoY.\n"
            f"         Please re-run with --growth-type MoM or --growth-type YoY."
        )

    # ── Filter per-ward per-category (agents.md enforcement: REFUSE aggregation)
    subset = df[(df["ward"] == ward) & (df["category"] == category)].copy()

    if subset.empty:
        sys.exit(
            f"[REFUSE] No data found for ward='{ward}' category='{category}'.\n"
            f"         Aggregation across all wards/categories is not allowed.\n"
            f"         Please specify an exact ward and category."
        )

    # ── Sort by period (chronological) ────────────────────────────────────────
    subset = subset.sort_values("period").reset_index(drop=True)

    # ── Identify null-spend rows (agents.md enforcement: FLAG every null) ─────
    null_mask = subset["actual_spend"].isna()

    print(f"[compute_growth] Ward     : {ward}")
    print(f"[compute_growth] Category : {category}")
    print(f"[compute_growth] Growth   : {growth_type}")
    print(f"[compute_growth] Rows     : {len(subset)} | "
          f"Null actual_spend: {null_mask.sum()}\n")

    # ── Determine which indices to skip (null row + its adjacent "next" row) ──
    # The period AFTER a null cannot use the null as a base — skip its formula.
    skip_formula_indices = set()
    for i in subset.index[null_mask]:
        skip_formula_indices.add(i)          # null row itself
        if i + 1 in subset.index:
            skip_formula_indices.add(i + 1)  # next row references null as base

    # ── Build lookup: period → spend (for YoY: period minus 12 months) ────────
    spend_by_period = subset.set_index("period")["actual_spend"].to_dict()

    # ── Compute growth row by row ──────────────────────────────────────────────
    records = []
    for i, row in subset.iterrows():
        period      = row["period"]
        spend_raw   = row["actual_spend"]
        notes_val   = row["notes"] if pd.notna(row["notes"]) else ""

        is_null     = pd.isna(spend_raw)
        null_flag   = "Y" if is_null else ""
        null_reason = notes_val if is_null else ""

        actual_spend_display = "NULL" if is_null else spend_raw

        # ── Skip formula if null or adjacent to null ───────────────────────────
        if i in skip_formula_indices:
            growth_pct = ""
            formula    = "NULL — not computed" if is_null else \
                         "Skipped — previous period is NULL"
        else:
            # ── Determine base period ──────────────────────────────────────────
            if growth_type == "MoM":
                prev_year  = int(period[:4])
                prev_month = int(period[5:7]) - 1
                if prev_month == 0:
                    prev_month = 12
                    prev_year -= 1
                base_period = f"{prev_year}-{prev_month:02d}"
            else:  # YoY
                base_period = f"{int(period[:4]) - 1}-{period[5:7]}"

            base_spend = spend_by_period.get(base_period)

            if base_spend is None or pd.isna(base_spend):
                # Base period doesn't exist in dataset or is null
                growth_pct = ""
                formula    = f"Base period {base_period} not available"
            else:
                pct        = (spend_raw - base_spend) / base_spend * 100
                sign       = "+" if pct >= 0 else ""
                growth_pct = f"{sign}{pct:.1f} %"
                formula    = (f"({spend_raw} − {base_spend}) / "
                              f"{base_spend} × 100 = {sign}{pct:.1f} %")

        records.append({
            "period":        period,
            "ward":          ward,
            "category":      category,
            "actual_spend":  actual_spend_display,
            "growth_pct":    growth_pct,
            "formula":       formula,
            "null_flag":     null_flag,
            "null_reason":   null_reason,
        })

    # ── Write CSV (agents.md intent: growth_output.csv) ───────────────────────
    out_df = pd.DataFrame(records, columns=[
        "period", "ward", "category", "actual_spend",
        "growth_pct", "formula", "null_flag", "null_reason"
    ])
    out_df.to_csv(output_path, index=False)

    # ── Print to stdout for quick verification ─────────────────────────────────
    print("[compute_growth] Output preview:")
    print(out_df.to_string(index=False))
    print(f"\n[compute_growth] Written to: {output_path}")

    # ── Reference verification check (README § Reference Values) ──────────────
    _verify_reference_values(out_df, ward, category, growth_type)


# ══════════════════════════════════════════════════════════════════════════════
#  REFERENCE VERIFICATION
#  Cross-checks README § Reference Values automatically at runtime.
# ══════════════════════════════════════════════════════════════════════════════
def _verify_reference_values(out_df: pd.DataFrame,
                              ward: str,
                              category: str,
                              growth_type: str) -> None:
    """
    If the run is for Ward 1 – Kasba | Roads & Pothole Repair | MoM,
    automatically validates the two README reference values.
    """
    if (ward == "Ward 1 \u2013 Kasba"
            and category == "Roads & Pothole Repair"
            and growth_type == "MoM"):

        checks = [
            ("2024-07", "+33.1 %"),
            ("2024-10", "\u221234.8 %"),
        ]
        print("\n[verify] README reference check:")
        for period, expected in checks:
            row = out_df[out_df["period"] == period]
            if row.empty:
                print(f"  [FAIL] {period} — row not found in output")
                continue
            actual = row.iloc[0]["growth_pct"].strip()
            # Normalise minus sign variants for comparison
            actual_norm   = actual.replace("\u2212", "-")
            expected_norm = expected.replace("\u2212", "-")
            status = "PASS" if actual_norm == expected_norm else "FAIL"
            print(f"  [{status}] {period}: expected {expected}, got {actual}")


# ══════════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT  (python app.py --input ... --ward ... --category ...
#                                  --growth-type MoM|YoY --output ...)
# ══════════════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Analyst — per-ward per-category only."
    )
    parser.add_argument("--input",       required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,
                        help='Ward name, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category",   required=True,
                        help='Category, e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", required=True, dest="growth_type",
                        choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-over-month) or "
                             "YoY (year-over-year). REQUIRED — never guessed.")
    parser.add_argument("--output",      required=True,
                        help="Output CSV path, e.g. growth_output.csv")

    args = parser.parse_args()

    # ── SKILL 1: load and validate dataset ────────────────────────────────────
    df = load_dataset(args.input)

    # ── SKILL 2: compute growth per-ward per-category ─────────────────────────
    compute_growth(
        df          = df,
        ward        = args.ward,
        category    = args.category,
        growth_type = args.growth_type,
        output_path = args.output,
    )


if __name__ == "__main__":
    main()
