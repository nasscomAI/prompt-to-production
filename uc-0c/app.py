import argparse
import pandas as pd
import sys


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes"
]


def refuse(message):
    print(f"❌ REFUSAL: {message}")
    sys.exit(1)


def load_dataset(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        refuse("Input file not found.")

    # Validate schema
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            refuse(f"Missing required column: {col}")

    # Identify null rows
    null_rows = df[df["actual_spend"].isna()]

    print("\n🔍 Null Value Report:")
    if null_rows.empty:
        print("No null values found.")
    else:
        for _, row in null_rows.iterrows():
            print(
                f"- {row['period']} | {row['ward']} | {row['category']} "
                f"| Reason: {row['notes']}"
            )

    return df


def compute_growth(df, ward, category, growth_type):
    # Enforce growth type
    if not growth_type:
        refuse("Growth type not specified. Please provide --growth-type (MoM or YoY).")

    if growth_type not in ["MoM"]:
        refuse("Only MoM growth is supported for this task.")

    # Filter strictly by ward and category
    filtered = df[(df["ward"] == ward) & (df["category"] == category)]

    if filtered.empty:
        refuse("No data found for given ward and category.")

    # Ensure no unintended aggregation
    if filtered["ward"].nunique() > 1 or filtered["category"].nunique() > 1:
        refuse("Aggregation across wards/categories detected. Refusing.")

    # Sort by period
    filtered = filtered.sort_values("period")

    output_rows = []

    prev_value = None

    for _, row in filtered.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        notes = row["notes"]

        # Case 1: current value is NULL
        if pd.isna(actual):
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "NOT COMPUTED",
                "formula": "N/A",
                "reason": notes
            })
            prev_value = None
            continue

        # Case 2: first valid value OR previous is NULL
        if prev_value is None:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "growth": "N/A",
                "formula": "N/A",
                "reason": "No previous value"
            })
            prev_value = actual
            continue

        # Compute MoM growth
        try:
            growth = ((actual - prev_value) / prev_value) * 100
            formula = f"(({actual} - {prev_value}) / {prev_value}) * 100"

            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "growth": f"{growth:.1f}%",
                "formula": formula,
                "reason": ""
            })

        except ZeroDivisionError:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "growth": "NOT COMPUTED",
                "formula": "Division by zero",
                "reason": "Previous value was zero"
            })

        prev_value = actual

    return pd.DataFrame(output_rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")

    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    # Load dataset
    df = load_dataset(args.input)

    # Compute growth
    result = compute_growth(df, args.ward, args.category, args.growth_type)

    # Save output
    result.to_csv(args.output, index=False)

    print(f"\n✅ Output saved to {args.output}")


if __name__ == "__main__":
    main()