import argparse
import os
import sys

import pandas as pd

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")

    df = pd.read_csv(filepath)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    null_rows = df[df["actual_spend"].isna()]
    null_list = []
    for _, row in null_rows.iterrows():
        null_list.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "null_reason": row["notes"] if pd.notna(row["notes"]) else "No reason provided",
        })

    print(f"Loaded {len(df)} rows from {filepath}")
    print(f"Null actual_spend count: {len(null_list)}")
    if null_list:
        print("Null rows:")
        for nr in null_list:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['null_reason']}")

    return df, null_list


def compute_growth(df, growth_type):
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"growth_type must be 'MoM' or 'YoY', got '{growth_type}'")

    wards = df["ward"].unique()
    categories = df["category"].unique()
    if len(wards) > 1:
        raise ValueError(f"Input spans multiple wards: {list(wards)}")
    if len(categories) > 1:
        raise ValueError(f"Input spans multiple categories: {list(categories)}")

    df = df.sort_values("period").reset_index(drop=True)

    results = []

    for i, (_, row) in enumerate(df.iterrows()):
        actual = row["actual_spend"]
        is_null = pd.isna(actual)
        null_reason = str(row["notes"]) if is_null and pd.notna(row["notes"]) else ""

        if growth_type == "MoM":
            if i == 0:
                formula = "N/A — no prior period"
                growth_rate = "NULL"
            elif is_null:
                formula = "N/A — actual_spend is NULL"
                growth_rate = "NULL"
            else:
                prev_actual = df.iloc[i - 1]["actual_spend"]
                if pd.isna(prev_actual):
                    formula = "N/A — prior period actual_spend is NULL"
                    growth_rate = "NULL"
                else:
                    growth_rate = round((actual - prev_actual) / prev_actual * 100, 2)
                    formula = f"(current ({actual}) - previous ({prev_actual})) / previous ({prev_actual}) * 100"
        else:
            if is_null:
                formula = "N/A — actual_spend is NULL"
                growth_rate = "NULL"
            else:
                current_year = int(row["period"][:4])
                current_month = row["period"][5:7]
                prev_year_period = f"{current_year - 1}-{current_month}"
                prev_row = df[df["period"] == prev_year_period]
                if prev_row.empty:
                    formula = "N/A — no prior year data available"
                    growth_rate = "NULL"
                else:
                    prev_actual = prev_row.iloc[0]["actual_spend"]
                    if pd.isna(prev_actual):
                        formula = "N/A — prior year actual_spend is NULL"
                        growth_rate = "NULL"
                    else:
                        growth_rate = round((actual - prev_actual) / prev_actual * 100, 2)
                        formula = f"(current ({actual}) - previous_year ({prev_actual})) / previous_year ({prev_actual}) * 100"

        results.append({
            "period": row["period"],
            "actual_spend": actual if not is_null else "NULL",
            "growth_rate": growth_rate,
            "null_flag": is_null,
            "null_reason": null_reason,
            "formula_used": formula,
        })

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="Ward budget growth computation")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category to filter")
    parser.add_argument("--growth-type", help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV path")

    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type is required. Specify 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)

    try:
        df, null_list = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)

    filtered = df[(df["ward"] == args.ward) & (df["category"] == args.category)]

    if filtered.empty:
        print(f"Error: No data found for ward '{args.ward}' and category '{args.category}'", file=sys.stderr)
        sys.exit(1)

    try:
        result = compute_growth(filtered, args.growth_type)
    except ValueError as e:
        print(f"Error computing growth: {e}", file=sys.stderr)
        sys.exit(1)

    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} rows to {args.output}")


if __name__ == "__main__":
    main()
