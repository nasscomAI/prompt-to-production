"""
UC-0C — Budget Growth Calculator
Computes per-period MoM or YoY growth for a single ward + category.
Uses pandas for all arithmetic — no LLM involved (avoids the "number that looks right" failure).
"""
import argparse
import csv
import sys
from pathlib import Path

import pandas as pd


def load_dataset(input_path: str) -> pd.DataFrame:
    """Load CSV, validate columns, report all null actual_spend rows before returning."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    df = pd.read_csv(path)
    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    null_rows = df[df["actual_spend"].isna()]
    if not null_rows.empty:
        print(f"\nNULL REPORT — {len(null_rows)} rows with missing actual_spend flagged before computation:")
        for _, row in null_rows.iterrows():
            note = row["notes"] if pd.notna(row["notes"]) and str(row["notes"]).strip() else "(no note)"
            print(f"  [{row['period']}] {row['ward']} / {row['category']} — {note}")
        print()
    else:
        print("NULL REPORT — No null actual_spend rows found.\n")

    return df


def compute_growth(df: pd.DataFrame, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for one ward + category.
    Shows formula in every row. Flags nulls — never computes a figure from a null.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"growth_type must be 'MoM' or 'YoY', got: {growth_type!r}")

    subset = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    if subset.empty:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'")

    subset = subset.sort_values("period").reset_index(drop=True)
    results = []

    for i, row in subset.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        note = row["notes"] if pd.notna(row["notes"]) and str(row["notes"]).strip() else ""

        # Null row — flag, never compute
        if pd.isna(actual):
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "FLAGGED — null actual_spend",
                "formula": "N/A",
                "notes": note,
            })
            continue

        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{actual:.1f}",
                    "growth": "N/A — first period",
                    "formula": "N/A — no prior period",
                    "notes": note,
                })
                continue

            prev_row = subset.iloc[i - 1]
            prev_actual = prev_row["actual_spend"]
            prev_period = prev_row["period"]

            if pd.isna(prev_actual):
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{actual:.1f}",
                    "growth": "FLAGGED — prior period is null, cannot compute MoM",
                    "formula": f"({actual:.1f} - NULL) / NULL",
                    "notes": note,
                })
                continue

            growth_val = (actual - prev_actual) / prev_actual * 100
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual:.1f}",
                "growth": f"{growth_val:+.1f}%",
                "formula": f"({actual:.1f} - {prev_actual:.1f}) / {prev_actual:.1f} = {growth_val:+.1f}%",
                "notes": note,
            })

        elif growth_type == "YoY":
            # Look for same month in the prior year
            year = int(period[:4])
            month = period[5:]
            prior_period = f"{year - 1}-{month}"
            prior_rows = subset[subset["period"] == prior_period]

            if prior_rows.empty:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{actual:.1f}",
                    "growth": "N/A — no prior year data in dataset",
                    "formula": f"Requires {prior_period} — not in dataset",
                    "notes": note,
                })
                continue

            prior_actual = prior_rows.iloc[0]["actual_spend"]
            if pd.isna(prior_actual):
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{actual:.1f}",
                    "growth": "FLAGGED — prior year period is null, cannot compute YoY",
                    "formula": f"({actual:.1f} - NULL) / NULL",
                    "notes": note,
                })
                continue

            growth_val = (actual - prior_actual) / prior_actual * 100
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual:.1f}",
                "growth": f"{growth_val:+.1f}%",
                "formula": f"({actual:.1f} - {prior_actual:.1f}) / {prior_actual:.1f} = {growth_val:+.1f}%",
                "notes": note,
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Budget category (exact match)")
    parser.add_argument("--growth-type", dest="growth_type", choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-on-month) or YoY (year-on-year)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    if not args.growth_type:
        print("ERROR: --growth-type is required. Please specify MoM or YoY.")
        print("Refusing to guess — MoM and YoY produce different numbers and the choice is yours.")
        sys.exit(1)

    df = load_dataset(args.input)

    print(f"Computing {args.growth_type} growth for:")
    print(f"  Ward    : {args.ward}")
    print(f"  Category: {args.category}\n")

    results = compute_growth(df, args.ward, args.category, args.growth_type)

    output_path = Path(args.output)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Console table
    print(f"{'Period':<10} {'Actual (Rs L)':>13} {'Growth':>14}  Formula")
    print("-" * 80)
    for r in results:
        print(f"{r['period']:<10} {r['actual_spend']:>12} {r['growth']:>14}  {r['formula']}")

    print(f"\nResults written to {output_path}")


if __name__ == "__main__":
    main()
