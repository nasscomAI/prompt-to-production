"""
UC-0C app.py — Budget Growth Calculator.

Computes period-over-period growth rates for municipal ward budget data.
Enforces per-ward per-category granularity, null flagging, formula
transparency, and mandatory growth-type specification.

See README.md for run command and expected behaviour.
"""

import argparse
import sys
import pandas as pd


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Reads the ward budget CSV, validates required columns, and reports
    every null actual_spend row before returning the DataFrame.
    """
    required_cols = {"period", "ward", "category", "budgeted_amount",
                     "actual_spend", "notes"}

    df = pd.read_csv(filepath)

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if len(df) == 0:
        raise ValueError("Dataset is empty — zero data rows after reading.")

    # --- Report nulls -------------------------------------------------------
    null_mask = df["actual_spend"].isna()
    null_rows = df[null_mask]
    print(f"\n{'='*60}")
    print(f"DATA QUALITY REPORT")
    print(f"{'='*60}")
    print(f"Total rows loaded        : {len(df)}")
    print(f"Null actual_spend rows   : {null_mask.sum()}")

    if not null_rows.empty:
        print(f"\nNull row details:")
        for _, row in null_rows.iterrows():
            reason = row["notes"] if pd.notna(row["notes"]) else "No reason provided"
            print(f"  • {row['period']} | {row['ward']} | "
                  f"{row['category']} — Reason: {reason}")
    print(f"{'='*60}\n")

    return df


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------
def compute_growth(df: pd.DataFrame, ward: str, category: str,
                   growth_type: str) -> pd.DataFrame:
    """
    Computes per-period growth for a specific ward + category + growth_type.
    Returns a table with the formula shown and null rows flagged.
    """
    # --- Validate growth_type -----------------------------------------------
    valid_types = {"MoM", "YoY"}
    if growth_type not in valid_types:
        raise ValueError(
            f"Invalid growth_type '{growth_type}'. "
            f"Valid choices: {sorted(valid_types)}"
        )

    # --- Validate ward ------------------------------------------------------
    valid_wards = sorted(df["ward"].unique())
    if ward not in valid_wards:
        raise ValueError(
            f"Ward '{ward}' not found. Valid wards:\n"
            + "\n".join(f"  • {w}" for w in valid_wards)
        )

    # --- Validate category --------------------------------------------------
    valid_cats = sorted(df["category"].unique())
    if category not in valid_cats:
        raise ValueError(
            f"Category '{category}' not found. Valid categories:\n"
            + "\n".join(f"  • {c}" for c in valid_cats)
        )

    # --- Filter & sort ------------------------------------------------------
    subset = (
        df[(df["ward"] == ward) & (df["category"] == category)]
        .copy()
        .sort_values("period")
        .reset_index(drop=True)
    )

    if subset["actual_spend"].isna().all():
        raise ValueError(
            f"All actual_spend values are null for "
            f"'{ward}' / '{category}'. No growth can be computed."
        )

    # --- Determine shift based on growth_type --------------------------------
    if growth_type == "MoM":
        shift_periods = 1
        formula_label = "MoM = (current - previous_month) / previous_month × 100"
    else:  # YoY
        shift_periods = 12
        formula_label = "YoY = (current - same_month_prev_year) / same_month_prev_year × 100"

    # --- Build output table --------------------------------------------------
    results = []
    for i, row in subset.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        note = row["notes"] if pd.notna(row["notes"]) else ""

        # Current row is null
        is_null = pd.isna(actual)
        null_flag = "NULL" if is_null else ""
        null_reason = note if is_null else ""

        # Find the previous period value
        idx_in_subset = subset.index.get_loc(i)
        prev_idx = idx_in_subset - shift_periods

        if prev_idx < 0:
            prev_spend = None
        else:
            prev_row = subset.iloc[prev_idx]
            prev_spend = prev_row["actual_spend"]

        prev_is_null = pd.isna(prev_spend) if prev_spend is not None else True

        # Compute growth
        if is_null or prev_is_null or prev_spend == 0:
            growth_pct = None
            formula_used = "N/A — null value(s) present" if (is_null or prev_is_null) else "N/A — division by zero"
        else:
            growth_pct = round((actual - prev_spend) / prev_spend * 100, 1)
            formula_used = formula_label

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual if not is_null else None,
            "previous_period_spend": prev_spend if not prev_is_null else None,
            "formula": formula_used,
            "growth_pct": growth_pct,
            "null_flag": null_flag,
            "null_reason": null_reason,
        })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Budget Growth Calculator — per-ward per-category growth rates"
    )
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True,
                        help="Ward name to filter (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True,
                        help="Category to filter (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="Growth type: MoM or YoY (REQUIRED)")
    parser.add_argument("--output", required=True,
                        help="Output CSV file path")

    args = parser.parse_args()

    # --- Enforcement: refuse if growth-type not specified --------------------
    if args.growth_type is None:
        print("ERROR: --growth-type is required. Please specify 'MoM' or 'YoY'.")
        print("       The system will not guess the growth type.")
        sys.exit(1)

    # --- Enforcement: refuse cross-ward / cross-category aggregation ---------
    #     (The CLI requires a single ward + category; this is structural.)

    # --- Load & validate ----------------------------------------------------
    print(f"Loading dataset from: {args.input}")
    df = load_dataset(args.input)

    # --- Compute growth -----------------------------------------------------
    print(f"Computing {args.growth_type} growth for:")
    print(f"  Ward     : {args.ward}")
    print(f"  Category : {args.category}")
    print()

    result = compute_growth(df, args.ward, args.category, args.growth_type)

    # --- Display results ----------------------------------------------------
    print(f"{'='*80}")
    print(f"GROWTH RESULTS — {args.growth_type}")
    print(f"{'='*80}")

    for _, row in result.iterrows():
        if row["null_flag"] == "NULL":
            print(f"  {row['period']}  |  actual_spend: NULL  |  "
                  f"⚠ FLAGGED — {row['null_reason']}  |  "
                  f"Growth: not computed")
        elif pd.notna(row["growth_pct"]):
            sign = "+" if row["growth_pct"] >= 0 else ""
            print(f"  {row['period']}  |  actual_spend: {row['actual_spend']:.1f}  |  "
                  f"prev: {row['previous_period_spend']:.1f}  |  "
                  f"Growth: {sign}{row['growth_pct']}%  |  "
                  f"Formula: {row['formula']}")
        else:
            spend_str = f"{row['actual_spend']:.1f}" if pd.notna(row['actual_spend']) else "N/A"
            print(f"  {row['period']}  |  actual_spend: {spend_str}  |  "
                  f"Growth: N/A (no prior period)")

    print(f"{'='*80}\n")

    # --- Save output --------------------------------------------------------
    result.to_csv(args.output, index=False)
    print(f"Output saved to: {args.output}")
    print(f"Rows written: {len(result)}")


if __name__ == "__main__":
    main()
