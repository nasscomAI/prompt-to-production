"""
UC-0C app.py — Budget Growth Calculator

Rules enforced:
- No aggregation across wards or categories
- Growth type must be specified
- Null values must be flagged
- Formula must be shown in output
"""

import argparse
import pandas as pd
import sys


def load_dataset(file_path):
    """Load dataset and validate structure"""

    df = pd.read_csv(file_path)

    required_columns = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # detect null rows
    null_rows = df[df["actual_spend"].isna()]

    if len(null_rows) > 0:
        print("Detected NULL actual_spend rows:")
        for _, row in null_rows.iterrows():
            print(
                f"{row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}"
            )

    return df


def compute_growth(df, ward, category, growth_type):
    """Compute growth values"""

    if growth_type not in ["MoM", "YoY"]:
        raise ValueError("growth-type must be MoM or YoY")

    # filter ward + category
    df = df[(df["ward"] == ward) & (df["category"] == category)]

    if df.empty:
        raise ValueError("No data found for specified ward and category")

    df = df.sort_values("period").reset_index(drop=True)

    results = []

    for i in range(len(df)):

        row = df.iloc[i]
        actual = row["actual_spend"]

        if pd.isna(actual):
            results.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": None,
                "growth": "FLAGGED",
                "formula": "Not computed due to null actual_spend",
                "flag": row["notes"],
            })
            continue

        if growth_type == "MoM":

            if i == 0:
                results.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": actual,
                    "growth": None,
                    "formula": "First month — no previous value",
                    "flag": "",
                })
                continue

            prev = df.iloc[i - 1]["actual_spend"]

            if pd.isna(prev):
                results.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": actual,
                    "growth": None,
                    "formula": "Previous value null — cannot compute",
                    "flag": "Previous period missing data",
                })
            else:
                growth = ((actual - prev) / prev) * 100

                results.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": actual,
                    "growth": round(growth, 2),
                    "formula": "((current_actual - previous_actual) / previous_actual) * 100",
                    "flag": "",
                })

        elif growth_type == "YoY":

            # look 12 months back
            if i < 12:
                results.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": actual,
                    "growth": None,
                    "formula": "No previous year value",
                    "flag": "",
                })
                continue

            prev = df.iloc[i - 12]["actual_spend"]

            if pd.isna(prev):
                results.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": actual,
                    "growth": None,
                    "formula": "Previous year value null",
                    "flag": "Previous year missing data",
                })
            else:
                growth = ((actual - prev) / prev) * 100

                results.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": actual,
                    "growth": round(growth, 2),
                    "formula": "((current_actual - last_year_actual) / last_year_actual) * 100",
                    "flag": "",
                })

    return pd.DataFrame(results)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward")
    parser.add_argument("--category")
    parser.add_argument("--growth-type")
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if not args.ward or not args.category:
        print("ERROR: Ward and Category must be specified.")
        sys.exit(1)

    if not args.growth_type:
        print("ERROR: You must specify --growth-type MoM or YoY")
        sys.exit(1)

    df = load_dataset(args.input)

    result = compute_growth(df, args.ward, args.category, args.growth_type)

    result.to_csv(args.output, index=False)

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()