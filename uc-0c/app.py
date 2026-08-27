import argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type not in ["MoM", "YoY"]:
        raise ValueError("Growth type must be MoM or YoY")

    df = pd.read_csv(args.input)

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
            raise ValueError(f"Missing column: {col}")

    filtered = df[
        (df["ward"] == args.ward) &
        (df["category"] == args.category)
    ].copy()

    filtered = filtered.sort_values("period")

    output_rows = []

    previous = None

    for _, row in filtered.iterrows():

        if pd.isna(row["actual_spend"]):
            output_rows.append({
                "period": row["period"],
                "actual_spend": "NULL",
                "growth": "NOT COMPUTED",
                "formula": "Null value detected",
                "notes": row["notes"]
            })
            previous = None
            continue

        current = row["actual_spend"]

        if previous is None:
            growth = "N/A"
            formula = "No previous month available"
        else:
            growth_value = ((current - previous) / previous) * 100

            growth = f"{growth_value:.1f}%"

            formula = f"(({current} - {previous}) / {previous}) * 100"

        output_rows.append({
            "period": row["period"],
            "actual_spend": current,
            "growth": growth,
            "formula": formula,
            "notes": row["notes"]
        })

        previous = current

    output_df = pd.DataFrame(output_rows)

    output_df.to_csv(args.output, index=False)

    print("Growth output generated successfully.")

if __name__ == "__main__":
    main()