"""
UC-0C app.py — Budget Growth Analyst
Computes MoM or YoY growth rates on ward-level municipal budget data.
See README.md for run command and expected behaviour.
"""

import argparse
import sys
import pandas as pd


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(filepath):
    """
    Reads the ward budget CSV, validates required columns, and reports
    null actual_spend rows (with reasons) before returning the DataFrame.
    """
    required_columns = [
        "period", "ward", "category",
        "budgeted_amount", "actual_spend", "notes",
    ]

    # --- Read file ---
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        sys.exit(f"ERROR: File not found — {filepath}")
    except Exception as exc:
        sys.exit(f"ERROR: Could not read file — {exc}")

    # --- Validate columns ---
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        sys.exit(f"ERROR: Missing required columns — {', '.join(missing)}")

    # --- Report nulls ---
    null_rows = df[df["actual_spend"].isna()]
    if not null_rows.empty:
        print(f"\n⚠  Found {len(null_rows)} null actual_spend row(s):\n")
        print(
            null_rows[["period", "ward", "category", "notes"]]
            .to_string(index=False)
        )
        print()

    return df


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------
def compute_growth(df, ward, category, growth_type):
    """
    Computes per-period growth rates for a specific ward + category.
    Returns a DataFrame with formula shown alongside each result.
    Null actual_spend periods are flagged and excluded from computation.
    """

    # --- Validate ward & category ---
    valid_wards = sorted(df["ward"].unique())
    valid_categories = sorted(df["category"].unique())

    if ward not in valid_wards:
        sys.exit(
            f"ERROR: Ward '{ward}' not found.\n"
            f"Valid wards: {', '.join(valid_wards)}"
        )
    if category not in valid_categories:
        sys.exit(
            f"ERROR: Category '{category}' not found.\n"
            f"Valid categories: {', '.join(valid_categories)}"
        )

    # --- Filter data ---
    subset = (
        df[(df["ward"] == ward) & (df["category"] == category)]
        .copy()
        .sort_values("period")
        .reset_index(drop=True)
    )

    if subset.empty:
        sys.exit(
            f"ERROR: No data for ward='{ward}', category='{category}'."
        )

    # --- Build output rows ---
    results = []

    for i, row in subset.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        notes = row["notes"] if pd.notna(row["notes"]) else ""

        # Null handling — flag and skip
        if pd.isna(actual):
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "previous_period_spend": "",
                "growth_rate_%": f"NULL — not computed ({notes})",
                "formula_used": "N/A — actual_spend is null",
            })
            continue

        # Determine previous period value
        prev_actual = None
        if growth_type == "MoM":
            # Look backwards for the nearest non-null row
            for j in range(i - 1, -1, -1):
                prev_row = subset.iloc[j]
                if pd.notna(prev_row["actual_spend"]):
                    prev_actual = prev_row["actual_spend"]
                    break
        elif growth_type == "YoY":
            # Same month, previous year (not applicable in single-year data)
            target_month = period[5:]  # MM part
            target_year = str(int(period[:4]) - 1)
            target_period = f"{target_year}-{target_month}"
            match = subset[
                (subset["period"] == target_period)
                & subset["actual_spend"].notna()
            ]
            if not match.empty:
                prev_actual = match.iloc[0]["actual_spend"]

        # Compute growth rate
        if prev_actual is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "previous_period_spend": "",
                "growth_rate_%": "N/A — no prior period",
                "formula_used": "N/A — first period or no prior data",
            })
        else:
            growth_rate = ((actual - prev_actual) / prev_actual) * 100
            formula = (
                f"({actual} - {prev_actual}) / {prev_actual} × 100 "
                f"= {growth_rate:+.1f}%"
            )
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "previous_period_spend": prev_actual,
                "growth_rate_%": f"{growth_rate:+.1f}%",
                "formula_used": formula,
            })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Analyst — per-ward, per-category growth rates",
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to analyse")
    parser.add_argument("--category", required=True, help="Budget category to analyse")
    parser.add_argument(
        "--growth-type",
        choices=["MoM", "YoY"],
        default=None,
        help="Growth calculation type: MoM (month-over-month) or YoY (year-over-year)",
    )
    parser.add_argument("--output", required=True, help="Output CSV path")

    args = parser.parse_args()

    # Enforcement: refuse if growth-type not specified
    if args.growth_type is None:
        sys.exit(
            "ERROR: --growth-type is required. "
            "Please specify MoM (month-over-month) or YoY (year-over-year)."
        )

    # Skill 1: load_dataset
    print(f"Loading dataset from: {args.input}")
    df = load_dataset(args.input)
    print(f"Loaded {len(df)} rows.\n")

    # Skill 2: compute_growth
    print(f"Computing {args.growth_type} growth for:")
    print(f"  Ward:     {args.ward}")
    print(f"  Category: {args.category}\n")

    result = compute_growth(df, args.ward, args.category, args.growth_type)

    # Save output
    result.to_csv(args.output, index=False)
    print(f"✅ Output written to: {args.output}")
    print(f"   {len(result)} rows generated.\n")

    # Display result
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
