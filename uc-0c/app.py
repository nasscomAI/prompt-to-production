"""
UC-0C — Growth Calculator for ward budget data.
Computes MoM or YoY growth for a single ward + category combination.
"""
import argparse
import sys

import numpy as np
import pandas as pd


def load_dataset(file_path):
    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")

    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    if df.empty:
        raise ValueError("CSV file is empty")

    null_mask = df["actual_spend"].isna()
    null_count = null_mask.sum()
    print(f"Rows with null actual_spend: {null_count}")
    if null_count > 0:
        null_rows = df[null_mask][["period", "ward", "category", "notes"]]
        for _, r in null_rows.iterrows():
            note = r["notes"] if pd.notna(r["notes"]) else ""
            print(f"  {r['period']} | {r['ward']} | {r['category']} | {note}")

    return df


def compute_growth(df, ward, category, growth_type):
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'.")

    if ward not in df["ward"].values:
        avail = sorted(df["ward"].unique())
        raise ValueError(f"Ward '{ward}' not found. Available wards: {avail}")
    if category not in df["category"].values:
        avail = sorted(df["category"].unique())
        raise ValueError(f"Category '{category}' not found. Available categories: {avail}")

    subset = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    subset = subset.sort_values("period").reset_index(drop=True)

    null_mask = subset["actual_spend"].isna()
    if null_mask.any():
        print(f"\nFlagged null actual_spend rows for '{ward}' / '{category}':")
        for _, r in subset[null_mask].iterrows():
            note = r["notes"] if pd.notna(r["notes"]) else "No reason provided"
            print(f"  {r['period']} — {note}")

    result = []
    prev_spend = None
    prev_period = None

    for _, row in subset.iterrows():
        cur = row["actual_spend"]

        if pd.isna(cur):
            result.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": np.nan,
                "growth_rate": np.nan,
                "formula": "NULL — not computed",
            })
            prev_spend = None
            prev_period = None
            continue

        if prev_spend is None or prev_period is None:
            result.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": cur,
                "growth_rate": np.nan,
                "formula": "N/A — no prior period",
            })
            prev_spend = cur
            prev_period = row["period"]
            continue

        if growth_type == "YoY":
            result.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": cur,
                "growth_rate": np.nan,
                "formula": "N/A — no prior year data",
            })
            prev_spend = cur
            prev_period = row["period"]
            continue

        growth_val = ((cur - prev_spend) / prev_spend) * 100
        formula_str = f"(({cur} - {prev_spend}) / {prev_spend}) × 100 = {growth_val:+.1f}%"

        result.append({
            "period": row["period"],
            "ward": ward,
            "category": category,
            "actual_spend": cur,
            "growth_rate": round(growth_val, 1),
            "formula": formula_str,
        })

        prev_spend = cur
        prev_period = row["period"]

    return pd.DataFrame(result)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type")
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type is required. Specify 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)

    df = load_dataset(args.input)
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    result_df.to_csv(args.output, index=False)
    print(f"\nOutput written to {args.output}")


if __name__ == "__main__":
    main()
