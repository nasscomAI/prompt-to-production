import argparse
import sys
import pandas as pd


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print(f"REFUSAL: Missing required columns: {missing}", file=sys.stderr)
        sys.exit(1)

    null_rows = df[df["actual_spend"].isna()]
    print(f"Null actual_spend rows found: {len(null_rows)}")
    for _, row in null_rows.iterrows():
        print(f"  - {row['period']} · {row['ward']} · {row['category']} · Reason: {row['notes']}")

    return df


def compute_growth(df: pd.DataFrame, ward: str, category: str, growth_type: str) -> pd.DataFrame:
    if growth_type not in ("MoM", "YoY"):
        print("REFUSAL: --growth-type must be 'MoM' or 'YoY'", file=sys.stderr)
        sys.exit(1)

    subset = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    if subset.empty:
        wards = df["ward"].unique().tolist()
        cats = df["category"].unique().tolist()
        print(f"REFUSAL: No data for ward='{ward}', category='{category}'", file=sys.stderr)
        print(f"Available wards: {wards}", file=sys.stderr)
        print(f"Available categories: {cats}", file=sys.stderr)
        sys.exit(1)

    subset = subset.sort_values("period").reset_index(drop=True)

    null_in_subset = subset[subset["actual_spend"].isna()]
    for _, row in null_in_subset.iterrows():
        print(f"FLAGGED NULL: {row['period']} · {row['ward']} · {row['category']} · Reason: {row['notes']}")

    results = []
    for i, row in subset.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        notes = row["notes"]

        if pd.isna(actual):
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_pct": "NOT COMPUTED",
                "formula": f"NULL actual_spend — {notes}"
            })
            continue

        if i == 0:
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth_pct": "N/A (baseline)",
                "formula": "N/A — baseline period"
            })
            continue

        if growth_type == "MoM":
            prior_idx = i - 1
        else:
            current_year = int(period[:4])
            current_month = int(period[5:])
            target_period = f"{current_year - 1}-{current_month:02d}"
            prior_matches = subset[subset["period"] == target_period]
            if prior_matches.empty:
                results.append({
                    "period": period,
                    "actual_spend": actual,
                    "growth_pct": "N/A (no prior year)",
                    "formula": f"YoY: no data for {target_period}"
                })
                continue
            prior_idx = prior_matches.index[0]

        prior_actual = subset.loc[prior_idx, "actual_spend"]
        if pd.isna(prior_actual):
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth_pct": "N/A (prior NULL)",
                "formula": f"{growth_type}: prior period actual_spend is NULL"
            })
            continue

        growth = ((actual - prior_actual) / prior_actual) * 100
        formula = f"(({actual} - {prior_actual}) / {prior_actual}) * 100 = {growth:.1f}%"
        results.append({
            "period": period,
            "actual_spend": actual,
            "growth_pct": f"{growth:.1f}%",
            "formula": formula
        })

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="Compute ward-level budget growth (MoM/YoY)")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    df = load_dataset(args.input)
    result = compute_growth(df, args.ward, args.category, args.growth_type)
    result.to_csv(args.output, index=False)
    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()