"""
UC-0C — Number That Looks Right
Compute per-period MoM growth for a single ward + category.
"""
import argparse
import sys

import pandas as pd


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"period": str, "ward": str, "category": str,
                                   "budgeted_amount": float, "notes": str},
                     keep_default_na=False)
    df["actual_spend"] = pd.to_numeric(df["actual_spend"], errors="coerce")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    print(f"Total rows loaded: {len(df)}", file=sys.stderr)

    null_mask = df["actual_spend"].isna()
    null_count = null_mask.sum()
    print(f"Null actual_spend rows: {null_count}", file=sys.stderr)
    if null_count > 0:
        null_rows = df.loc[null_mask, ["period", "ward", "category", "notes"]]
        for _, r in null_rows.iterrows():
            print(f"  NULL row — {r['period']} | {r['ward']} | {r['category']} | {r['notes']}", file=sys.stderr)

    return df


def compute_growth(df: pd.DataFrame, ward: str, category: str, growth_type: str) -> pd.DataFrame:
    if not growth_type:
        print("Error: --growth-type is required. Specify 'MoM' to proceed.", file=sys.stderr)
        sys.exit(1)

    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth type '{growth_type}'. Only 'MoM' is supported.")

    subset = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    if subset.empty:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")

    subset = subset.sort_values("period").reset_index(drop=True)
    if subset.duplicated(subset="period").any():
        raise ValueError(f"Duplicate period entries for ward '{ward}' and category '{category}'.")

    results = []
    prev_spend = None

    for idx, row in subset.iterrows():
        period = row["period"]
        spend = row["actual_spend"]
        notes = row["notes"]
        null_flag = pd.isna(spend)

        if null_flag:
            growth_rate = ""
            formula = f"NULL — not computed ({notes})"
            null_reason = notes
        elif prev_spend is None:
            growth_rate = "N/A"
            formula = "No previous period"
            null_reason = ""
        else:
            raw = ((spend - prev_spend) / prev_spend) * 100
            growth_rate = f"{raw:+.1f}%"
            formula = f"(({spend} - {prev_spend}) / {prev_spend}) * 100 = {raw:+.1f}%"
            null_reason = ""

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{spend:.1f}" if not null_flag else "",
            "growth_rate": growth_rate,
            "formula": formula,
            "null_flag": "True" if null_flag else "False",
            "null_reason": null_reason,
        })

        if not null_flag:
            prev_spend = spend

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="UC-0C — MoM growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category to filter")
    parser.add_argument("--growth-type", default=None, help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type is required. Specify 'MoM' to proceed.", file=sys.stderr)
        sys.exit(1)

    df = load_dataset(args.input)
    result = compute_growth(df, args.ward, args.category, args.growth_type)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} rows to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
