import argparse
import pandas as pd


def load_dataset(input_path):
    df = pd.read_csv(input_path)

    required_columns = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    return df


def compute_growth(df, ward, category, growth_type):
    if not growth_type:
        raise ValueError(
            "growth_type must be specified."
        )

    filtered = df[
        (df["ward"] == ward)
        &
        (df["category"] == category)
        ].copy()

    filtered = filtered.sort_values("period")

    results = []

    previous_value = None

    for _, row in filtered.iterrows():

        current = row["actual_spend"]

        if pd.isna(current):
            results.append({
                "period": row["period"],
                "actual_spend": "",
                "formula": "",
                "growth_pct": "",
                "flag": "NULL_SPEND",
                "reason": row["notes"]
            })
            previous_value = None
            continue

        if previous_value is None:
            results.append({
                "period": row["period"],
                "actual_spend": current,
                "formula": "N/A",
                "growth_pct": "",
                "flag": "",
                "reason": ""
            })
        else:

            growth = (
                             (current - previous_value)
                             / previous_value
                     ) * 100

            formula = (
                f"(({current}-{previous_value})/"
                f"{previous_value})*100"
            )

            results.append({
                "period": row["period"],
                "actual_spend": current,
                "formula": formula,
                "growth_pct": round(growth, 2),
                "flag": "",
                "reason": ""
            })

        previous_value = current

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

    result = compute_growth(
        df,
        args.ward,
        args.category,
        args.growth_type
    )

    result.to_csv(
        args.output,
        index=False
    )

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()