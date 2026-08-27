"""
UC-0C app.py — Growth calculation tool for ward budget data.
"""
import argparse
import sys
import pandas as pd

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend"]


def load_dataset(path):
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if df.empty:
        raise ValueError("CSV file is empty")
    null_mask = df["actual_spend"].isna()
    print(f"Null actual_spend rows: {null_mask.sum()}")
    for _, row in df[null_mask].iterrows():
        note = row.get("notes", "") or ""
        print(f"  {row['period']} | {row['ward']} | {row['category']} | {note}")
    return df


def compute_growth(df, ward, category, growth_type):
    filtered = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    if filtered.empty:
        return pd.DataFrame()
    filtered = filtered.sort_values("period").reset_index(drop=True)
    filtered["period_dt"] = pd.to_datetime(filtered["period"])
    results = []

    for i, row in filtered.iterrows():
        null_flag = ""
        growth_val = ""
        formula_str = ""
        if pd.isna(row["actual_spend"]):
            null_flag = row.get("notes", "") or "No data"
            formula_str = ""
            growth_val = ""
        else:
            current_spend = row["actual_spend"]
            prev_spend = None
            prev_period = None

            if growth_type == "MoM":
                if i > 0:
                    prev_row = filtered.iloc[i - 1]
                    if not pd.isna(prev_row["actual_spend"]):
                        prev_spend = prev_row["actual_spend"]
                        prev_period = prev_row["period"]
            elif growth_type == "YoY":
                current_dt = row["period_dt"]
                prior_dt = current_dt - pd.DateOffset(years=1)
                prior_str = prior_dt.strftime("%Y-%m")
                prev_rows = filtered[filtered["period"] == prior_str]
                if not prev_rows.empty and not pd.isna(prev_rows.iloc[0]["actual_spend"]):
                    prev_spend = prev_rows.iloc[0]["actual_spend"]
                    prev_period = prior_str

            if prev_spend is not None and prev_spend != 0:
                growth_val = round(((current_spend - prev_spend) / prev_spend) * 100, 2)
                formula_str = (
                    f"(({row['period']} spend - {prev_period} spend) / "
                    f"{prev_period} spend) * 100"
                )
            else:
                growth_val = ""
                formula_str = "insufficient prior data"

        results.append({
            "ward": ward,
            "category": category,
            "period": row["period"],
            "actual_spend": row["actual_spend"] if not pd.isna(row["actual_spend"]) else "",
            "growth": growth_val,
            "formula": formula_str,
            "null_flag": null_flag,
        })

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="Compute ward budget growth")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    if args.growth_type not in ("MoM", "YoY"):
        print("Error: --growth-type is required. Must be 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)

    try:
        df = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    result = compute_growth(df, args.ward, args.category, args.growth_type)
    if result.empty:
        print(f"Error: No data found for ward '{args.ward}' and category '{args.category}'", file=sys.stderr)
        sys.exit(1)

    result.to_csv(args.output, index=False)
    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()
