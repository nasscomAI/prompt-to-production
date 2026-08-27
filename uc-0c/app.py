"""
UC-0C app.py — Budget Growth Analyst Agent
Computes per-ward, per-category MoM or YoY growth on actual_spend.

Enforcement rules (from agents.md):
  1. Never aggregate across wards or categories — refuse if asked.
  2. Flag every null actual_spend row — report null reason from notes.
  3. Show formula used in every output row.
  4. If --growth-type not specified — refuse and ask.
"""

import argparse
import sys
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Reads the ward_budget.csv file, validates required columns, and reports
    every null actual_spend row with its reason from the notes column.
    Returns the validated DataFrame.
    """
    REQUIRED_COLUMNS = [
        "period", "ward", "category",
        "budgeted_amount", "actual_spend", "notes",
    ]

    # --- Read file ---
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"ERROR: File not found — {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read CSV — {e}")
        sys.exit(1)

    if df.empty:
        print("ERROR: The CSV file is empty.")
        sys.exit(1)

    # --- Validate columns ---
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print(f"ERROR: Missing required columns: {missing}")
        sys.exit(1)

    # --- Report nulls ---
    null_mask = df["actual_spend"].isna()
    null_rows = df[null_mask]
    null_count = len(null_rows)

    print("=" * 70)
    print("DATASET LOADED SUCCESSFULLY")
    print(f"  Total rows       : {len(df)}")
    print(f"  Unique wards     : {df['ward'].nunique()}")
    print(f"  Unique categories: {df['category'].nunique()}")
    print(f"  Null actual_spend: {null_count}")
    print("=" * 70)

    if null_count > 0:
        print("\n⚠  NULL actual_spend ROWS DETECTED — these will be EXCLUDED")
        print("   from growth computation:\n")
        for _, row in null_rows.iterrows():
            reason = row["notes"] if pd.notna(row["notes"]) else "No reason provided"
            print(f"   • {row['period']}  |  {row['ward']}  |  "
                  f"{row['category']}  |  Reason: {reason}")
        print()

    return df


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------
def compute_growth(
    df: pd.DataFrame,
    ward: str,
    category: str,
    growth_type: str,
) -> pd.DataFrame:
    """
    Filters the dataset for the given ward + category, sorts by period,
    and computes MoM or YoY growth on actual_spend.
    Returns a DataFrame with columns:
      ward, category, period, actual_spend, growth_rate, formula_used
    """

    # --- Validate ward ---
    available_wards = sorted(df["ward"].unique())
    if ward not in available_wards:
        print(f"ERROR: Ward '{ward}' not found in dataset.")
        print(f"  Available wards: {available_wards}")
        sys.exit(1)

    # --- Validate category ---
    available_cats = sorted(df["category"].unique())
    if category not in available_cats:
        print(f"ERROR: Category '{category}' not found in dataset.")
        print(f"  Available categories: {available_cats}")
        sys.exit(1)

    # --- Filter ---
    subset = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    subset = subset.sort_values("period").reset_index(drop=True)

    if subset.empty:
        print(f"ERROR: No data for ward='{ward}', category='{category}'.")
        sys.exit(1)

    # Determine the shift (lag) based on growth type
    if growth_type == "MoM":
        lag = 1          # compare to previous month
        label = "MoM"
    else:  # YoY
        lag = 12         # compare to same month previous year
        label = "YoY"

    # --- Build output rows (for CSV) and console lines (with formulas) ---
    output_rows = []     # clean data for CSV
    console_lines = []   # detailed lines with formulas for console
    growth_col = f"{label} Growth"

    for i, row in subset.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        note = row["notes"] if pd.notna(row["notes"]) else ""

        # Current period has null actual_spend
        if pd.isna(actual):
            output_rows.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (₹ lakh)": "NULL",
                growth_col: "NULL — must be flagged, not computed",
            })
            console_lines.append(
                f"  {period}  |  NULL  |  Skipped — null actual_spend: {note}"
            )
            continue

        # Look up the previous period value
        idx_in_subset = subset.index.get_loc(i)
        prev_idx = idx_in_subset - lag

        if prev_idx < 0:
            # No prior period available for comparison
            output_rows.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (₹ lakh)": actual,
                growth_col: "N/A",
            })
            console_lines.append(
                f"  {period}  |  {actual}  |  N/A — no prior period for {label}"
            )
            continue

        prev_row = subset.iloc[prev_idx]
        prev_actual = prev_row["actual_spend"]
        prev_period = prev_row["period"]

        if pd.isna(prev_actual):
            # Previous period was null — cannot compute growth
            prev_note = prev_row["notes"] if pd.notna(prev_row["notes"]) else ""
            output_rows.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (₹ lakh)": actual,
                growth_col: "NULL — must be flagged, not computed",
            })
            console_lines.append(
                f"  {period}  |  {actual}  |  N/A — prior period "
                f"{prev_period} is null: {prev_note}"
            )
            continue

        # --- Compute growth rate ---
        growth_rate = ((actual - prev_actual) / prev_actual) * 100
        growth_rate_rounded = round(growth_rate, 1)

        sign = "+" if growth_rate_rounded >= 0 else ""
        formula = (
            f"{label} Growth = ({actual} − {prev_actual}) / {prev_actual} × 100 "
            f"= {sign}{growth_rate_rounded}%"
        )

        output_rows.append({
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": actual,
            growth_col: f"{sign}{growth_rate_rounded}%",
        })
        console_lines.append(
            f"  {period}  |  {actual}  |  {sign}{growth_rate_rounded}%  "
            f"|  Formula: {formula}"
        )

    result_df = pd.DataFrame(output_rows)
    return result_df, console_lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description=(
            "UC-0C Budget Growth Analyst — computes per-ward, per-category "
            "MoM or YoY growth on actual_spend."
        )
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the ward_budget.csv file.",
    )
    parser.add_argument(
        "--ward", required=True,
        help='Exact ward name, e.g. "Ward 1 – Kasba".',
    )
    parser.add_argument(
        "--category", required=True,
        help='Exact category name, e.g. "Roads & Pothole Repair".',
    )
    parser.add_argument(
        "--growth-type", dest="growth_type", default=None,
        choices=["MoM", "YoY"],
        help="Growth type: MoM (month-over-month) or YoY (year-over-year).",
    )
    parser.add_argument(
        "--output", default="growth_output.csv",
        help="Output CSV file path (default: growth_output.csv).",
    )

    args = parser.parse_args()

    # ---- Enforcement: refuse if --growth-type not specified ----
    if args.growth_type is None:
        print("ERROR: --growth-type is required.")
        print("  Please specify either MoM (month-over-month) or "
              "YoY (year-over-year).")
        print("  Example: --growth-type MoM")
        sys.exit(1)

    # ---- Enforcement: refuse cross-ward / cross-category aggregation ----
    if args.ward.lower() in ("all", "any", "*"):
        print("ERROR: Cross-ward aggregation is not permitted.")
        print("  This agent operates at per-ward granularity.")
        print("  Please specify a single ward name.")
        sys.exit(1)

    if args.category.lower() in ("all", "any", "*"):
        print("ERROR: Cross-category aggregation is not permitted.")
        print("  This agent operates at per-category granularity.")
        print("  Please specify a single category name.")
        sys.exit(1)

    # ---- Skill: load_dataset ----
    df = load_dataset(args.input)

    # ---- Skill: compute_growth ----
    result, console_lines = compute_growth(
        df, args.ward, args.category, args.growth_type
    )

    # ---- Print result to console (with formulas for traceability) ----
    print(f"\n{'=' * 70}")
    print(f"GROWTH REPORT  —  {args.growth_type}")
    print(f"  Ward     : {args.ward}")
    print(f"  Category : {args.category}")
    print(f"{'=' * 70}")
    for line in console_lines:
        print(line)
    print(f"{'=' * 70}")

    # ---- Save clean CSV (no formulas — values only) ----
    result.to_csv(args.output, index=False)
    print(f"\n✅ Output saved to: {args.output}")
    print(f"   Columns: {list(result.columns)}")


if __name__ == "__main__":
    main()
