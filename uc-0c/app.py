import argparse
import pandas as pd

def load_dataset(path):
    df = pd.read_csv(path)

    required = ["period","ward","category","budgeted_amount","actual_spend","notes"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column {col}")

    return df


def compute_growth(df, ward, category, growth_type):

    if growth_type != "MoM":
        raise ValueError("Only MoM supported for this exercise")

    df = df[(df["ward"] == ward) & (df["category"] == category)].copy()

    df = df.sort_values("period")

    results = []

    prev = None

    for _, row in df.iterrows():

        current = row["actual_spend"]

        if pd.isna(current):
            results.append({
                "period": row["period"],
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "NULL",
                "note": row["notes"]
            })
            prev = None
            continue

        if prev is None:
            results.append({
                "period": row["period"],
                "actual_spend": current,
                "growth": "N/A",
                "formula": "No previous month",
                "note": ""
            })
        else:
            growth = ((current - prev) / prev) * 100

            formula = f"(({current} - {prev}) / {prev}) * 100"

            results.append({
                "period": row["period"],
                "actual_spend": current,
                "growth": round(growth,2),
                "formula": formula,
                "note": ""
            })

        prev = current

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

    result = compute_growth(df, args.ward, args.category, args.growth_type)

    result.to_csv(args.output, index=False)

    print("Growth output written to", args.output)


if __name__ == "__main__":
    main()