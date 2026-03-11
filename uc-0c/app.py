import pandas as pd
import argparse

def load_dataset(path):
    df = pd.read_csv(path)

    required = ["period","ward","category","budgeted_amount","actual_spend","notes"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    null_rows = df[df["actual_spend"].isna()]

    if not null_rows.empty:
        print("Null rows detected:")
        print(null_rows[["period","ward","category","notes"]])

    return df


def compute_growth(df, ward, category, growth_type):

    if growth_type != "MoM":
        raise ValueError("Only MoM supported in this exercise")

    subset = df[(df["ward"] == ward) & (df["category"] == category)]

    if subset.empty:
        raise ValueError("No data for that ward/category")

    subset = subset.sort_values("period")

    results = []
    prev = None

    for _, row in subset.iterrows():

        period = row["period"]
        spend = row["actual_spend"]

        if pd.isna(spend):
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_percent": "",
                "formula": "NULL value – growth not computed",
                "flag": "NEEDS_REVIEW"
            })
            prev = None
            continue

        if prev is None:
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth_percent": "",
                "formula": "first period – no previous month",
                "flag": ""
            })
        else:
            growth = ((spend - prev) / prev) * 100
            formula = f"(({spend}-{prev})/{prev})*100"

            results.append({
                "period": period,
                "actual_spend": spend,
                "growth_percent": round(growth,2),
                "formula": formula,
                "flag": ""
            })

        prev = spend

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

    table = compute_growth(df, args.ward, args.category, args.growth_type)

    table.to_csv(args.output, index=False)

    print("Growth table written →", args.output)


if __name__ == "__main__":
    main()