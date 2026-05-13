import pandas as pd
import argparse


def load_dataset(file_path):
    df = pd.read_csv(file_path)

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
            raise ValueError(f"Missing required column: {col}")

    null_rows = df[df["actual_spend"].isnull()]

    if not null_rows.empty:
        print("\nNull rows found:")
        print(null_rows[["period", "ward", "category", "notes"]])

    return df


def compute_growth(df, ward, category, growth_type):

    if growth_type is None:
        raise ValueError("growth-type is required. Do not guess.")

    if growth_type != "MoM":
        raise ValueError("Only MoM growth is supported.")

    filtered = df[
        (df["ward"] == ward) &
        (df["category"] == category)
    ].copy()

    filtered = filtered.sort_values("period")

    results = []

    previous_value = None

    for _, row in filtered.iterrows():

        current_value = row["actual_spend"]

        if pd.isna(current_value):
            growth = "NULL"
            formula = "Cannot compute because actual_spend is NULL"

        elif previous_value is None or pd.isna(previous_value):
            growth = "N/A"
            formula = "No previous month available"

        else:
            growth_value = (
                (current_value - previous_value)
                / previous_value
            ) * 100

            growth = round(growth_value, 1)

            formula = (
                f"(({current_value} - {previous_value}) / "
                f"{previous_value}) * 100"
            )

        results.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": current_value,
            "MoM_growth_percent": growth,
            "formula": formula
        })

        previous_value = current_value

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

    result_df = compute_growth(
        df,
        args.ward,
        args.category,
        args.growth_type
    )

    result_df.to_csv(args.output, index=False)

    print("\nGrowth analysis completed.")
    print(result_df)


if __name__ == "__main__":
    main()