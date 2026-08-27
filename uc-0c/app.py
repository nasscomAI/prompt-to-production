"""
UC-0C app.py — Budget Growth Analysis Agent
Implements load_dataset and compute_growth skills defined in skills.md.
Agent behaviour governed by agents.md (RICE: role, intent, context, enforcement).

Run command (from README.md):
    python app.py \\
      --input ../data/budget/ward_budget.csv \\
      --ward "Ward 1 – Kasba" \\
      --category "Roads & Pothole Repair" \\
      --growth-type MoM \\
      --output growth_output.csv
"""

import argparse
import sys
import pandas as pd


# ---------------------------------------------------------------------------
# REQUIRED COLUMNS (source of truth for validation)
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ---------------------------------------------------------------------------
# SKILL: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(filepath: str) -> tuple[pd.DataFrame, list[dict]]:
    """
    Reads the ward_budget CSV, validates all required columns are present,
    and reports null actual_spend rows (with reason) before returning.

    Returns
    -------
    df : pd.DataFrame
        Full validated dataset.
    null_report : list[dict]
        One entry per null row: {period, ward, category, null_reason}.

    Raises
    ------
    SystemExit
        If the file is not found or required columns are missing — halts immediately,
        does not proceed with partial data.
    """
    # --- File load ---
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"\n[ERROR] File not found: {filepath}", file=sys.stderr)
        print("        Check the --input path and try again.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"\n[ERROR] Could not read file: {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Column validation ---
    missing = REQUIRED_COLUMNS - set(df.columns.str.strip())
    if missing:
        print(f"\n[ERROR] Dataset is missing required columns: {sorted(missing)}", file=sys.stderr)
        print("        Required: " + ", ".join(sorted(REQUIRED_COLUMNS)), file=sys.stderr)
        sys.exit(1)

    # Normalise column names (strip whitespace)
    df.columns = df.columns.str.strip()

    # --- Null report (ENFORCEMENT: flag every null before computing) ---
    null_mask = df["actual_spend"].isna()
    null_rows = df[null_mask]
    null_report = [
        {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "null_reason": str(row["notes"]).strip() if pd.notna(row["notes"]) else "No reason provided",
        }
        for _, row in null_rows.iterrows()
    ]

    # Surface null report to the user immediately
    print(f"\n[load_dataset] Loaded {len(df)} rows from: {filepath}")
    print(f"[load_dataset] Null actual_spend count: {len(null_report)}")
    if null_report:
        print("[load_dataset] Flagged null rows (will NOT be computed):")
        for n in null_report:
            print(f"               • {n['period']} | {n['ward']} | {n['category']}")
            print(f"                 Reason: {n['null_reason']}")
    else:
        print("[load_dataset] No null rows detected.")

    return df, null_report


# ---------------------------------------------------------------------------
# SKILL: compute_growth
# ---------------------------------------------------------------------------
def compute_growth(
    df: pd.DataFrame,
    ward: str,
    category: str,
    growth_type: str,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Computes per-period growth (MoM or YoY) for the given ward + category.

    Returns
    -------
    result_df : pd.DataFrame
        Columns: period, actual_spend, growth_pct, formula
        One row per non-null period.
    skipped : list[dict]
        Null periods that were flagged/skipped (not computed).

    Raises
    ------
    SystemExit
        If growth_type is not "MoM" or "YoY", or if there are fewer than
        two non-null data points for the selected slice.
    """
    # --- ENFORCEMENT: refuse if growth_type is missing or invalid ---
    if growth_type is None:
        print(
            "\n[ERROR] --growth-type was not specified. "
            "Please provide 'MoM' or 'YoY' — this agent never guesses.",
            file=sys.stderr,
        )
        sys.exit(1)

    if growth_type.upper() not in ("MOM", "YOY"):
        print(
            f"\n[ERROR] Invalid --growth-type '{growth_type}'. "
            "Accepted values: MoM, YoY. "
            "This agent never defaults — please specify explicitly.",
            file=sys.stderr,
        )
        sys.exit(1)

    growth_type = growth_type.upper()  # normalise

    # --- ENFORCEMENT: operate strictly at ward + category level (no aggregation) ---
    slice_df = df[(df["ward"] == ward) & (df["category"] == category)].copy()

    if slice_df.empty:
        print(
            f"\n[ERROR] No rows found for ward='{ward}' / category='{category}'.",
            file=sys.stderr,
        )
        print(
            "        Available wards:      " + ", ".join(sorted(df["ward"].unique())),
            file=sys.stderr,
        )
        print(
            "        Available categories: " + ", ".join(sorted(df["category"].unique())),
            file=sys.stderr,
        )
        sys.exit(1)

    # Sort chronologically
    slice_df = slice_df.sort_values("period").reset_index(drop=True)

    # Separate null rows (flagged/skipped)
    null_mask = slice_df["actual_spend"].isna()
    skipped = [
        {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "null_reason": str(row["notes"]).strip() if pd.notna(row["notes"]) else "No reason provided",
        }
        for _, row in slice_df[null_mask].iterrows()
    ]

    valid_df = slice_df[~null_mask].copy()

    # --- Minimum data check ---
    if len(valid_df) < 2:
        print(
            f"\n[ERROR] Cannot compute growth: fewer than 2 non-null data points "
            f"for ward='{ward}' / category='{category}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    valid_df["actual_spend"] = pd.to_numeric(valid_df["actual_spend"], errors="coerce")

    # --- Growth computation ---
    rows = []

    if growth_type == "MOM":
        # Month-over-Month: (current - previous) / previous  *  100
        for i, row in valid_df.iterrows():
            idx_in_valid = valid_df.index.get_loc(i)
            if idx_in_valid == 0:
                # First row — no previous period, cannot compute
                rows.append(
                    {
                        "period": row["period"],
                        "actual_spend": row["actual_spend"],
                        "growth_pct": None,
                        "formula": "N/A (first period — no prior month)",
                    }
                )
            else:
                prev_row = valid_df.iloc[idx_in_valid - 1]
                prev_val = prev_row["actual_spend"]
                curr_val = row["actual_spend"]
                if prev_val == 0:
                    growth = None
                    formula = f"({curr_val} - {prev_val}) / {prev_val} — division by zero, skipped"
                else:
                    growth = round((curr_val - prev_val) / prev_val * 100, 2)
                    formula = f"({curr_val} - {prev_val}) / {prev_val} × 100 = {growth:+.2f}%"
                rows.append(
                    {
                        "period": row["period"],
                        "actual_spend": curr_val,
                        "growth_pct": growth,
                        "formula": formula,
                    }
                )

    else:  # YOY
        # Year-over-Year: same month, current year vs prior year
        # Since the dataset is a single year (2024), we compare Jan→Jan etc.
        # across wards for demonstration; for a multi-year dataset this would
        # compare 2024-MM to 2023-MM. Here we note YoY cannot be computed for
        # a single-year dataset and surface that clearly.
        print(
            "\n[WARNING] The dataset covers a single year (2024). "
            "YoY growth requires two calendar years of data. "
            "Returning MoM-equivalent table with YoY formula notation instead.",
            file=sys.stderr,
        )
        for i, row in valid_df.iterrows():
            idx_in_valid = valid_df.index.get_loc(i)
            if idx_in_valid == 0:
                rows.append(
                    {
                        "period": row["period"],
                        "actual_spend": row["actual_spend"],
                        "growth_pct": None,
                        "formula": "N/A (first period — no prior year equivalent)",
                    }
                )
            else:
                prev_row = valid_df.iloc[idx_in_valid - 1]
                prev_val = prev_row["actual_spend"]
                curr_val = row["actual_spend"]
                if prev_val == 0:
                    growth = None
                    formula = f"YoY: ({curr_val} - {prev_val}) / {prev_val} — division by zero, skipped"
                else:
                    growth = round((curr_val - prev_val) / prev_val * 100, 2)
                    formula = (
                        f"YoY approx: ({curr_val} - {prev_val}) / {prev_val} × 100 = {growth:+.2f}%"
                    )
                rows.append(
                    {
                        "period": row["period"],
                        "actual_spend": curr_val,
                        "growth_pct": growth,
                        "formula": formula,
                    }
                )

    result_df = pd.DataFrame(rows, columns=["period", "actual_spend", "growth_pct", "formula"])
    return result_df, skipped


# ---------------------------------------------------------------------------
# MAIN — CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Per-ward, per-category budget growth analysis agent."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument(
        "--growth-type",
        default=None,
        help="Growth type: MoM or YoY (REQUIRED — agent refuses to guess)",
    )
    parser.add_argument("--output", required=True, help="Output CSV filename")
    args = parser.parse_args()

    # ENFORCEMENT: refuse immediately if --growth-type is not provided
    if args.growth_type is None:
        print(
            "\n[REFUSED] --growth-type was not provided. "
            "This agent requires an explicit growth type: MoM or YoY.\n"
            "Rerun with --growth-type MoM  or  --growth-type YoY.",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Skill 1: load_dataset ---
    df, null_report = load_dataset(args.input)

    # --- Skill 2: compute_growth ---
    print(
        f"\n[compute_growth] Computing {args.growth_type} growth for: "
        f"ward='{args.ward}' | category='{args.category}'"
    )
    result_df, skipped = compute_growth(df, args.ward, args.category, args.growth_type)

    # --- Surface skipped/null rows in the growth scope ---
    if skipped:
        print(f"[compute_growth] Null rows in this ward/category slice (not computed):")
        for s in skipped:
            print(f"               • {s['period']} — Reason: {s['null_reason']}")

    # --- Print result table to stdout ---
    print(f"\n[Result] {args.growth_type} Growth — {args.ward} / {args.category}")
    print("-" * 80)
    for _, row in result_df.iterrows():
        pct_display = f"{row['growth_pct']:+.2f}%" if pd.notna(row["growth_pct"]) else "N/A"
        print(f"  {row['period']} | spend: {row['actual_spend']} | growth: {pct_display}")
        print(f"           formula: {row['formula']}")
    print("-" * 80)

    # --- Write output CSV ---
    result_df.to_csv(args.output, index=False)
    print(f"\n[Output] Written to: {args.output}")
    print(f"         Rows written: {len(result_df)} (computed) + {len(skipped)} (null/skipped flagged above)")


if __name__ == "__main__":
    main()
