import argparse
import pandas as pd

def load_dataset(file_path):
    df = pd.read_csv(file_path)

    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    null_rows = df[df["actual_spend"].isna()]
    if not null_rows.empty:
        print("Null rows detected:")
        print(null_rows[["period", "ward", "category", "notes"]])

    return df

def compute_growth(df, ward, category, growth_type):
    if growth_type != "MoM":
        raise ValueError("Only MoM growth supported for this task.")

    df = df[(df["ward"] == ward) & (df["category"] == category)]
    df = df.sort_values("period")

    results = []
    prev = None

    for _, row in df.iterrows():
        period = row["period"]
        actual = row["actual_spend"]

        if pd.isna(actual):
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "FLAGGED_NULL",
                "formula": "N/A"
            })
            prev = None
            continue

        if prev is None:
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth": "N/A",
                "formula": "First period"
            })
        else:
            growth = ((actual - prev) / prev) * 100
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth": f"{growth:.2f}%",
                "formula": "(current - previous) / previous * 100"
            })

        prev = actual

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

if __name__ == "__main__":
    main()
