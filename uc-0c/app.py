"""
UC-0C app.py — Per-ward per-category MoM/YoY growth calculator.
"""
import argparse
import sys
import pandas as pd
import numpy as np


def load_dataset(filepath):
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")

    required = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["actual_spend"] = pd.to_numeric(df["actual_spend"], errors="coerce")

    null_mask = df["actual_spend"].isna()
    null_rows = []
    for _, row in df[null_mask].iterrows():
        null_rows.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "notes": row["notes"] if pd.notna(row["notes"]) else ""
        })

    print(f"Loaded {len(df)} rows, {len(null_rows)} null actual_spend rows found.")
    for nr in null_rows:
        print(f"  Null: {nr['period']} | {nr['ward']} | {nr['category']} \u2014 {nr['notes']}")

    return df, null_rows


def compute_growth(df, ward, category, growth_type):
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"growth_type must be 'MoM' or 'YoY', got '{growth_type}'")

    cat_df = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    if cat_df.empty:
        return pd.DataFrame(columns=["period", "ward", "category", "actual_spend", "previous_spend", "growth_pct", "formula", "note"])

    cat_df["period_dt"] = pd.to_datetime(cat_df["period"] + "-01")
    cat_df = cat_df.sort_values("period_dt").reset_index(drop=True)

    results = []
    for i, row in cat_df.iterrows():
        current_spend = row["actual_spend"]
        current_note = row["notes"] if pd.notna(row["notes"]) else ""

        if growth_type == "MoM":
            prev_row = cat_df.iloc[i - 1] if i > 0 else None
        else:
            prev_period = row["period_dt"] - pd.DateOffset(months=12)
            match = cat_df[cat_df["period_dt"] == prev_period]
            prev_row = match.iloc[0] if len(match) > 0 else None

        if prev_row is not None:
            previous_spend = prev_row["actual_spend"]
        else:
            previous_spend = np.nan

        curr_is_null = pd.isna(current_spend)
        prev_is_null = pd.isna(previous_spend)

        if curr_is_null:
            growth_pct = "NULL"
            note = current_note
            formula = "N/A"
        elif prev_is_null:
            growth_pct = "NULL"
            note = current_note if current_note else f"No prior {growth_type} period available"
            formula = "N/A"
        else:
            pct = ((current_spend - previous_spend) / previous_spend) * 100
            growth_pct = f"{pct:+.1f}%"
            formula = f"(({current_spend:g} - {previous_spend:g}) / {previous_spend:g}) * 100"
            note = current_note

        results.append({
            "period": row["period"],
            "ward": ward,
            "category": category,
            "actual_spend": current_spend if not curr_is_null else "",
            "previous_spend": previous_spend if not prev_is_null else "",
            "growth_pct": growth_pct,
            "formula": formula,
            "note": note,
        })

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="Compute per-ward per-category growth rates.")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type is required (MoM or YoY)", file=sys.stderr)
        sys.exit(1)

    if args.ward.lower() in ("all", "overall", "total", "every"):
        print("Error: Aggregation across wards/categories is not supported.", file=sys.stderr)
        sys.exit(1)

    if args.category.lower() in ("all", "overall", "total", "every"):
        print("Error: Aggregation across wards/categories is not supported.", file=sys.stderr)
        sys.exit(1)

    df, null_rows = load_dataset(args.input)

    result_df = compute_growth(df, args.ward, args.category, args.growth_type)

    if result_df.empty:
        print(f"No data found for ward '{args.ward}' and category '{args.category}'.")
        result_df.to_csv(args.output, index=False)
        return

    result_df.to_csv(args.output, index=False)
    print(f"Output written to {args.output} ({len(result_df)} rows)")


if __name__ == "__main__":
    main()
