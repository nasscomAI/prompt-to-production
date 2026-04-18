import argparse
import pandas as pd

def load_dataset(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise Exception(f"Error loading file: {e}")

    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    for col in required_columns:
        if col not in df.columns:
            raise Exception(f"Missing required column: {col}")

    # Identify null rows
    null_rows = df[df["actual_spend"].isnull()]
    if not null_rows.empty:
        print("⚠️ Null values found:")
        print(null_rows[["period", "ward", "category", "notes"]])

    return df


def compute_growth(df, ward, category, growth_type):
    if not growth_type:
        raise Exception("Growth type not specified. Refusing to guess.")

    # Filter data
    filtered = df[(df["ward"] == ward) & (df["category"] == category)].copy()

    if filtered.empty:
        raise Exception("No data found for given ward and category.")

    filtered = filtered.sort_values("period")

    results = []

    prev_value = None

    for index, row in filtered.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        note = row["notes"]

        if pd.isnull(actual):
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "Not computed",
                "formula": f"NULL value — {note}"
            })
            prev_value = None
            continue

        if prev_value is None:
            growth = "N/A"
            formula = "First value — no previous data"
        else:
            growth_value = ((actual - prev_value) / prev_value) * 100
            growth = f"{round(growth_value, 2)}%"
            formula = f"(({actual} - {prev_value}) / {prev_value}) * 100"

        results.append({
            "period": period,
            "actual_spend": actual,
            "growth": growth,
            "formula": formula
        })

        prev_value = actual

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
    print(f"✅ Output saved to {args.output}")


if __name__ == "__main__":
    main()
