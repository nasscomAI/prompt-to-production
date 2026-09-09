"""
UC-0C app.py — Ward/category budget growth calculator.

Computes MoM or YoY growth for a single ward + category from the
infrastructure budget dataset. Refuses to aggregate across wards/categories,
refuses to guess a growth type, and flags (rather than silently skips) any
row with a null actual_spend value.
"""
import argparse
import sys
import pandas as pd

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(path: str, ward: str, category: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        print(f"ERROR: Dataset is missing required column(s): {missing_cols}")
        sys.exit(1)

    valid_wards = sorted(df["ward"].unique())
    valid_categories = sorted(df["category"].unique())

    if ward not in valid_wards:
        print(f"ERROR: Ward '{ward}' not found in dataset. Valid wards are: {valid_wards}")
        sys.exit(1)

    if category not in valid_categories:
        print(f"ERROR: Category '{category}' not found in dataset. Valid categories are: {valid_categories}")
        sys.exit(1)

    filtered = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    filtered = filtered.sort_values("period").reset_index(drop=True)

    null_rows = filtered[filtered["actual_spend"].isna()]
    if len(null_rows) > 0:
        print(f"NOTICE: {len(null_rows)} row(s) with null actual_spend found for this ward/category:")
        for _, row in null_rows.iterrows():
            print(f"  - {row['period']}: {row['notes']}")
    else:
        print("No null actual_spend rows found for this ward/category.")

    return filtered


def compute_growth(df: pd.DataFrame, growth_type: str) -> pd.DataFrame:
    if growth_type not in ("MoM", "YoY"):
        print(f"ERROR: --growth-type must be exactly 'MoM' or 'YoY'. Got: '{growth_type}'")
        sys.exit(1)

    df = df.copy()
    shift_amount = 1 if growth_type == "MoM" else 12
    formula_label = (
        "(current_actual - previous_month_actual) / previous_month_actual * 100"
        if growth_type == "MoM"
        else "(current_actual - same_month_last_year_actual) / same_month_last_year_actual * 100"
    )

    growth_pct = []
    status = []
    formula_used = []

    for i in range(len(df)):
        current = df.loc[i, "actual_spend"]

        if pd.isna(current):
            growth_pct.append(None)
            status.append("flagged_null")
            formula_used.append("n/a — actual_spend is null: " + str(df.loc[i, "notes"]))
            continue

        prev_index = i - shift_amount
        if prev_index < 0:
            growth_pct.append(None)
            status.append("flagged_null")
            formula_used.append("n/a — no prior period available for this growth type")
            continue

        previous = df.loc[prev_index, "actual_spend"]

        if pd.isna(previous):
            growth_pct.append(None)
            status.append("flagged_null")
            formula_used.append("n/a — baseline period actual_spend is null, cannot compute")
            continue

        pct = (current - previous) / previous * 100
        growth_pct.append(round(pct, 1))
        status.append("computed")
        formula_used.append(formula_label)

    df["growth_pct"] = growth_pct
    df["status"] = status
    df["formula_used"] = formula_used

    return df[["period", "ward", "category", "budgeted_amount", "actual_spend",
               "growth_pct", "status", "formula_used", "notes"]]


def main():
    parser = argparse.ArgumentParser(description="Compute ward/category budget growth.")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name to analyze")
    parser.add_argument("--category", required=True, help="Exact category name to analyze")
    parser.add_argument("--growth-type", required=False, default=None,
                         help="Must be 'MoM' or 'YoY'. Required — will not default.")
    parser.add_argument("--output", required=True, help="Path to write output CSV")

    args = parser.parse_args()

    if args.growth_type is None:
        print("ERROR: --growth-type is required. Please specify 'MoM' or 'YoY'. Refusing to guess.")
        sys.exit(1)

    filtered = load_dataset(args.input, args.ward, args.category)
    result = compute_growth(filtered, args.growth_type)

    result.to_csv(args.output, index=False)
    print(f"\nOutput written to {args.output}")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()