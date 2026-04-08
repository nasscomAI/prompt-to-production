"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
import pandas as pd
import sys


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes"
]


def load_dataset(path):
    df = pd.read_csv(path)

    # Validate columns
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            print(f"Missing required column: {col}")
            sys.exit(1)

    # Show null rows
    null_rows = df[df["actual_spend"].isna()]

    if len(null_rows) > 0:
        print("\n⚠ Null actual_spend rows detected:\n")

        for _, r in null_rows.iterrows():
            print(
                f"{r['period']} | {r['ward']} | {r['category']} "
                f"→ NULL (Reason: {r['notes']})"
            )

    return df


def compute_growth(df, ward, category, growth_type):

    if growth_type is None:
        print("Growth type must be specified (MoM)")
        sys.exit(1)

    # filter by ward and category
    df = df[(df["ward"] == ward) & (df["category"] == category)].copy()

    if df.empty:
        print("No data found for this ward/category")
        sys.exit(1)

    df = df.sort_values("period")

    prev = None
    output = []

    for _, row in df.iterrows():

        current = row["actual_spend"]

        # null case
        if pd.isna(current):
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "NULL",
                "growth_percent": "FLAGGED",
                "formula": "NULL value → growth not computed"
            })
            prev = None
            continue

        # first row
        if prev is None:
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current,
                "growth_percent": "N/A",
                "formula": "First period"
            })
            prev = current
            continue

        # MoM growth
        if growth_type == "MoM":
            growth = ((current - prev) / prev) * 100
            formula = f"(({current} - {prev}) / {prev}) * 100"
        else:
            print("Unsupported growth type")
            sys.exit(1)

        output.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": current,
            "growth_percent": round(growth, 2),
            "formula": formula
        })

        prev = current

    return pd.DataFrame(output)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    df = load_dataset(args.input)

    result = compute_growth(
        df,
        args.ward,
        args.category,
        args.growth_type
    )

    result.to_csv(args.output, index=False)

    print(f"\n✅ Output written to {args.output}")


if __name__ == "__main__":
    main()
