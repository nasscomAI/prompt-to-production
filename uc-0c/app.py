import argparse
import pandas as pd


def load_dataset(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Show null rows (important for audit)
    null_rows = df[df["actual_spend"].isna()]
    if not null_rows.empty:
        print("⚠ Null rows detected:")
        print(null_rows[["period", "ward", "category", "notes"]])

    return df


def compute_growth(df, ward, category, growth_type):
    if not growth_type:
        raise ValueError("Growth type must be specified (MoM or YoY)")

    if growth_type != "MoM":
        raise ValueError("Only MoM growth is supported")

    # STRICT FILTER (no aggregation)
    df_filtered = df[(df["ward"] == ward) & (df["category"] == category)].copy()

    if df_filtered.empty:
        raise ValueError("No data found for given ward and category")

    df_filtered = df_filtered.sort_values("period")

    results = []
    prev_value = None

    for _, row in df_filtered.iterrows():
        period = row["period"]
        value = row["actual_spend"]
        note = row["notes"]

        # NULL handling
        if pd.isna(value):
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "NA",
                "formula": "NA",
                "flag": f"NULL value — {note}"
            })
            prev_value = None
            continue

        # First valid row
        if prev_value is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": value,
                "growth": "NA",
                "formula": "NA (no previous value)",
                "flag": ""
            })
            prev_value = value
            continue

        # MoM Growth Calculation
        growth = ((value - prev_value) / prev_value) * 100
        formula = f"(({value} - {prev_value}) / {prev_value}) * 100"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": value,
            "growth": round(growth, 2),
            "formula": formula,
            "flag": ""
        })

        prev_value = value

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    df = load_dataset(args.input)

    result_df = compute_growth(
        df,
        args.ward,
        args.category,
        args.growth_type
    )

    result_df.to_csv(args.output, index=False)

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()
