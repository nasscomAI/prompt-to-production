import argparse
import pandas as pd


def compute_growth(df):
    results = []

    for i in range(1, len(df)):
        current = df.iloc[i]
        previous = df.iloc[i - 1]

        period = current["period"]
        current_val = current["actual_spend"]
        prev_val = previous["actual_spend"]

        if pd.isna(current_val) or pd.isna(prev_val):
            results.append({
                "period": period,
                "actual_spend": current_val,
                "formula": "NULL — computation skipped",
                "growth_percentage": "NULL"
            })
        else:
            growth = ((current_val - prev_val) / prev_val) * 100

            formula = f"(({current_val} - {prev_val}) / {prev_val}) * 100"

            results.append({
                "period": period,
                "actual_spend": current_val,
                "formula": formula,
                "growth_percentage": round(growth, 2)
            })

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type != "MoM":
        raise ValueError("Only MoM growth supported")

    df = pd.read_csv(args.input)

    df = df[(df["ward"] == args.ward) & (df["category"] == args.category)]

    df = df.sort_values("period")

    growth_df = compute_growth(df)

    growth_df.to_csv(args.output, index=False)

    print(f"Growth table saved to: {args.output}")


if __name__ == "__main__":
    main()
