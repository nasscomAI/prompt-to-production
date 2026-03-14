"""
UC-0C — Budget Growth Calculator
Computes MoM or YoY growth per ward per category from ward_budget.csv.
Refuses to aggregate, refuses to guess growth-type, flags all nulls.
"""

import argparse
import sys
import pandas as pd


# ─────────────────────────────────────────────
# SKILL: load_dataset
# ─────────────────────────────────────────────

def load_dataset(filepath: str) -> pd.DataFrame:
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    try:
        df = pd.read_csv(filepath, dtype={"notes": str})
    except FileNotFoundError:
        print(f"ERROR: File not found — {filepath}", file=sys.stderr)
        sys.exit(1)

    missing = required_columns - set(df.columns)
    if missing:
        print(f"ERROR: CSV is missing required columns: {missing}", file=sys.stderr)
        sys.exit(1)

    df["period"] = pd.to_datetime(df["period"], format="%Y-%m")

    null_rows = df[df["actual_spend"].isna()]
    if not null_rows.empty:
        print(f"\n[WARNING] NULL ROWS DETECTED ({len(null_rows)} rows) — these will NOT be computed:\n")
        for _, row in null_rows.iterrows():
            reason = row["notes"] if pd.notna(row["notes"]) else "No reason given"
            print(f"   • {row['period'].strftime('%Y-%m')} | {row['ward']} | {row['category']}")
            print(f"     Reason: {reason}")
        print()
    else:
        print("[OK] No null actual_spend values found.\n")

    return df


# ─────────────────────────────────────────────
# SKILL: compute_growth
# ─────────────────────────────────────────────

def compute_growth(df: pd.DataFrame, ward: str, category: str, growth_type: str) -> pd.DataFrame:
    available_wards = df["ward"].unique().tolist()
    if ward not in available_wards:
        print(f"ERROR: Ward '{ward}' not found.\nAvailable: {available_wards}", file=sys.stderr)
        sys.exit(1)

    available_cats = df["category"].unique().tolist()
    if category not in available_cats:
        print(f"ERROR: Category '{category}' not found.\nAvailable: {available_cats}", file=sys.stderr)
        sys.exit(1)

    subset = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    subset = subset.sort_values("period").reset_index(drop=True)

    if subset.empty:
        print(f"ERROR: No data for ward='{ward}' category='{category}'.", file=sys.stderr)
        sys.exit(1)

    results = []

    if growth_type == "MoM":
        for i, row in subset.iterrows():
            period_str = row["period"].strftime("%Y-%m")
            current = row["actual_spend"]

            if i == 0:
                # BUG FIX: first-period null must also be flagged (enforcement rule #2)
                flag = f"NULL: {row['notes']}" if pd.isna(current) else ""
                spend = "NULL" if pd.isna(current) else current
                results.append({"period": period_str, "actual_spend": spend,
                                 "growth_%": None, "formula": "N/A (first period)", "flag": flag})
                continue

            prev_row = subset.iloc[i - 1]
            prev = prev_row["actual_spend"]
            prev_period = prev_row["period"].strftime("%Y-%m")

            if pd.isna(current):
                results.append({"period": period_str, "actual_spend": "NULL", "growth_%": None,
                                 "formula": "NULL — not computed", "flag": f"NULL: {row['notes']}"})
            elif pd.isna(prev):
                results.append({"period": period_str, "actual_spend": round(current, 2), "growth_%": None,
                                 "formula": f"({current} - NULL) / NULL — cannot compute",
                                 "flag": f"Prior period {prev_period} is NULL"})
            else:
                growth = ((current - prev) / prev) * 100
                results.append({"period": period_str, "actual_spend": round(current, 2),
                                 "growth_%": round(growth, 1),
                                 "formula": f"({current} - {prev}) / {prev} × 100 = {round(growth,1)}%",
                                 "flag": ""})

    elif growth_type == "YoY":
        # BUG FIX: entire YoY computation loop was missing — only validation existed before
        years = subset["period"].dt.year.unique()
        if len(years) < 2:
            print(f"ERROR: YoY requires data from 2+ years. Dataset only has: {sorted(years)}", file=sys.stderr)
            sys.exit(1)

        for _, row in subset.iterrows():
            period_str = row["period"].strftime("%Y-%m")
            current = row["actual_spend"]
            prior_year_period = row["period"] - pd.DateOffset(years=1)
            prior_rows = subset[subset["period"] == prior_year_period]

            if prior_rows.empty:
                flag = f"NULL: {row['notes']}" if pd.isna(current) else ""
                spend = "NULL" if pd.isna(current) else round(current, 2)
                results.append({"period": period_str, "actual_spend": spend,
                                 "growth_%": None, "formula": "N/A (no prior year period)", "flag": flag})
                continue

            prev = prior_rows.iloc[0]["actual_spend"]
            prev_period = prior_rows.iloc[0]["period"].strftime("%Y-%m")

            if pd.isna(current):
                results.append({"period": period_str, "actual_spend": "NULL", "growth_%": None,
                                 "formula": "NULL — not computed", "flag": f"NULL: {row['notes']}"})
            elif pd.isna(prev):
                results.append({"period": period_str, "actual_spend": round(current, 2), "growth_%": None,
                                 "formula": f"({current} - NULL) / NULL — cannot compute",
                                 "flag": f"Prior year period {prev_period} is NULL"})
            else:
                growth = ((current - prev) / prev) * 100
                results.append({"period": period_str, "actual_spend": round(current, 2),
                                 "growth_%": round(growth, 1),
                                 "formula": f"({current} - {prev}) / {prev} × 100 = {round(growth,1)}%",
                                 "flag": ""})

    return pd.DataFrame(results)


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", dest="growth_type", choices=["MoM", "YoY"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.growth_type is None:
        print("\n[ERROR] REFUSED: --growth-type not specified.", file=sys.stderr)
        print("   Provide --growth-type MoM or --growth-type YoY. Never guessed.\n", file=sys.stderr)
        sys.exit(1)

    print(f"Loading: {args.input}")
    df = load_dataset(args.input)

    print(f"Computing {args.growth_type} | Ward: {args.ward} | Category: {args.category}\n")
    result = compute_growth(df, args.ward, args.category, args.growth_type)

    print(result.to_string(index=False))
    result.to_csv(args.output, index=False)
    print(f"\n[SUCCESS] Saved to: {args.output}")


if __name__ == "__main__":
    main()