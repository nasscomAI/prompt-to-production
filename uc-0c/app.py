import argparse
import pandas as pd
import sys


def load_dataset(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception:
        print("Error: Could not read dataset.")
        sys.exit(1)

    required_columns = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes"
    ]

    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Missing required column: {col}")
            sys.exit(1)

    return df


def compute_growth(df, ward, category, growth_type):

    if not growth_type:
        print("Error: --growth-type must be specified.")
        sys.exit(1)

    filtered = df[(df["ward"] == ward) & (df["category"] == category)]

    if filtered.empty:
        print("Error: No data found for specified ward and category.")
        sys.exit(1)

    filtered = filtered.sort_values("period")

    results = []
    previous_value = None

    for _, row in filtered.iterrows():

        period = row["period"]
        spend = row["actual_spend"]
        note = row["notes"]

        if pd.isna(spend):
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_percent": "FLAGGED",
                "formula": "NULL value — growth not computed",
                "notes": note
            })
            previous_value = None
            continue

        if previous_value is None:
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth_percent": "N/A",
                "formula": "No previous value",
                "notes": ""
            })
        else:
            growth = ((spend - previous_value) / previous_value) * 100
            formula = f"(({spend} - {previous_value}) / {previous_value}) * 100"

            results.append({
                "period": period,
                "actual_spend": spend,
                "growth_percent": round(growth, 2),
                "formula": formula,
                "notes": ""
            })

        previous_value = spend

    return pd.DataFrame(results)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    df = load_dataset(args.input)

    output_df = compute_growth(
        df,
        args.ward,
        args.category,
        args.growth_type
    )

    output_df.to_csv(args.output, index=False)

    print("Growth output generated successfully.")


if __name__ == "__main__":
    main()