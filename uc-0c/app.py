import pandas as pd
import argparse

def compute_growth(df):
    results = []

    df = df.sort_values("period")

    prev_value = None

    for _, row in df.iterrows():
        current = row["actual_spend"]

        if pd.isna(current) or prev_value is None or pd.isna(prev_value):
            growth = None
        else:
            try:
                growth = (current - prev_value) / prev_value
            except:
                growth = None

        results.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": current,
            "growth": growth
        })

        if not pd.isna(current):
            prev_value = current

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", default="MoM")
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    df = pd.read_csv(args.input)

    # Filter
    df_filtered = df[
        (df["ward"] == args.ward) &
        (df["category"] == args.category)
    ]

    if df_filtered.empty:
        print("No data found for given ward/category")
        return

    result_df = compute_growth(df_filtered)

    result_df.to_csv(args.output, index=False)

    print("Growth analysis saved to", args.output)


if __name__ == "__main__":
    main()
