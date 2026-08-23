"""
UC-0C app.py — Number That Looks Right
Processes budget CSV with strict enforcement of aggregation rules,
null handling, and formula transparency.
"""
import argparse
import sys
import pandas as pd


def load_dataset(csv_path: str) -> tuple:
    """Reads CSV, validates columns, reports null count and which rows before returning."""
    df = pd.read_csv(csv_path)

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Identify nulls: standard nan or empty string
    null_mask = df["actual_spend"].isna() | (df["actual_spend"].astype(str).str.strip() == "")
    null_count = int(null_mask.sum())
    
    # Extract null rows with details
    null_rows = df.loc[null_mask, ["ward", "category", "period", "notes"]]
    
    # Mapping for detailed reporting
    null_reasons = {}
    for _, row in null_rows.iterrows():
        key = (row["ward"], row["category"], row["period"])
        note = str(row["notes"]).strip() if pd.notna(row["notes"]) else ""
        null_reasons[key] = note if note else "null actual_spend"

    return df, null_count, null_rows, null_reasons


def compute_growth(df: pd.DataFrame, ward: str, category: str, growth_type: str) -> pd.DataFrame:
    """Takes ward + category + growth_type, returns per-period table with formula shown."""
    subset = df[(df["ward"] == ward) & (df["category"] == category)].copy()

    if subset.empty:
        raise ValueError(f"No data for ward='{ward}', category='{category}'")

    # Check for nulls in the specific requested subset
    null_mask = subset["actual_spend"].isna() | (subset["actual_spend"].astype(str).str.strip() == "")
    if null_mask.any():
        raise ValueError(
            f"Null actual_spend found for ward='{ward}', category='{category}'. "
            "Flag null rows before computing."
        )

    subset = subset.sort_values("period")
    subset["actual_spend"] = pd.to_numeric(subset["actual_spend"])

    if growth_type == "MoM":
        subset["growth_value"] = subset["actual_spend"].pct_change() * 100
        formula = "MoM growth = (current - previous) / previous * 100"
    elif growth_type == "YoY":
        # Check if we have enough data for YoY
        if len(subset) <= 12:
            subset["growth_value"] = None # Not enough data
        else:
            subset["growth_value"] = subset["actual_spend"].pct_change(periods=12) * 100
        formula = "YoY growth = (current - same month last year) / same month last year * 100"
    else:
        raise ValueError(f"Unknown growth_type: {growth_type}. Use 'MoM' or 'YoY'.")

    subset["formula_shown"] = formula
    return subset[["period", "actual_spend", "growth_value", "formula_shown"]]


def main():
    parser = argparse.ArgumentParser(description="UC-0C: Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name filter")
    parser.add_argument("--category", required=True, help="Category name filter")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    try:
        df, null_count, null_rows, null_reasons = load_dataset(args.input)

        if null_count > 0:
            print(f"WARNING: {null_count} null actual_spend row(s) found in total dataset:")
            for _, row in null_rows.iterrows():
                reason = null_reasons.get((row["ward"], row["category"], row["period"]), "null")
                print(f"  - {row['ward']} | {row['category']} | {row['period']}: {reason}")

        result = compute_growth(df, args.ward, args.category, args.growth_type)

        result.to_csv(args.output, index=False)
        print(f"Output written to {args.output}")
        print(f"Formula: {result['formula_shown'].iloc[0]}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()