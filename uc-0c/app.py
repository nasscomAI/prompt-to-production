"""
UC-0C app.py — Budget growth computation.
See README.md for run command and expected behaviour.
"""
import argparse
import sys
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(path):
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        sys.exit(f"Error: missing required columns: {missing}")
    df["actual_spend"] = pd.to_numeric(df["actual_spend"], errors="coerce")
    null_rows = df[df["actual_spend"].isna()]
    print(f"Dataset loaded: {len(df)} rows, {len(null_rows)} null actual_spend values")
    if len(null_rows) > 0:
        print("Null rows:")
        for _, r in null_rows.iterrows():
            note = r["notes"] if pd.notna(r["notes"]) else "No explanation given"
            print(f"  {r['period']} | {r['ward']} | {r['category']} | {note}")
    return df


def compute_growth(df, ward, category, growth_type):
    subset = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    if len(subset) == 0:
        sys.exit(f"Error: no data found for ward '{ward}' and category '{category}'")
    subset = subset.sort_values("period").reset_index(drop=True)
    results = []
    for i, row in subset.iterrows():
        actual = row["actual_spend"]
        if pd.isna(actual):
            note = row["notes"] if pd.notna(row["notes"]) else "No explanation given"
            results.append({
                "period": row["period"],
                "actual_spend": "NULL",
                "growth": f"NOT COMPUTED — {note}",
                "formula": f"NOT COMPUTED — {note}"
            })
            continue
        if i == 0:
            results.append({
                "period": row["period"],
                "actual_spend": f"{actual:.1f}",
                "growth": "N/A (first period)",
                "formula": "No previous period for comparison"
            })
            continue
        prev_actual = subset.iloc[i - 1]["actual_spend"]
        if pd.isna(prev_actual):
            results.append({
                "period": row["period"],
                "actual_spend": f"{actual:.1f}",
                "growth": "N/A (previous period null)",
                "formula": "Cannot compute growth — previous period actual_spend is NULL"
            })
            continue
        if growth_type == "MoM":
            growth_val = ((actual - prev_actual) / prev_actual) * 100
            sign = "+" if growth_val >= 0 else ""
            results.append({
                "period": row["period"],
                "actual_spend": f"{actual:.1f}",
                "growth": f"{sign}{growth_val:.1f}%",
                "formula": f"(({actual:.1f} - {prev_actual:.1f}) / {prev_actual:.1f}) * 100 = {sign}{growth_val:.1f}%"
            })
        elif growth_type == "YoY":
            growth_val = ((actual - prev_actual) / prev_actual) * 100
            sign = "+" if growth_val >= 0 else ""
            results.append({
                "period": row["period"],
                "actual_spend": f"{actual:.1f}",
                "growth": f"{sign}{growth_val:.1f}%",
                "formula": f"(({actual:.1f} - {prev_actual:.1f}) / {prev_actual:.1f}) * 100 = {sign}{growth_val:.1f}%"
            })
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="Budget growth computation")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=False, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    if args.growth_type not in ("MoM", "YoY"):
        sys.exit("Error: --growth-type is required and must be 'MoM' or 'YoY'. Refusing to guess.")

    df = load_dataset(args.input)
    result = compute_growth(df, args.ward, args.category, args.growth_type)
    result.to_csv(args.output, index=False)
    print(f"\nOutput written to {args.output}")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
