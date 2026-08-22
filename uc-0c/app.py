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

    # Growth type must be explicitly supported
    if args.growth_type != "MoM":
        print("REFUSED: Only explicit MoM growth is supported.")
        return

    # Load dataset
    try:
        df = pd.read_csv(args.input)
    except Exception as e:
        print(f"ERROR: Could not read input file: {e}")
        return

    # Validate required columns
    required_columns = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes"
    ]

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        print(f"ERROR: Missing required columns: {missing_columns}")
        return

    # Refuse all-ward aggregation
    if args.ward.lower() in ["all", "all wards", "all-ward"]:
        print("REFUSED: Aggregation across wards is not allowed.")
        return

    # Filter requested ward and category
    filtered = df[
        (df["ward"] == args.ward) &
        (df["category"] == args.category)
    ].copy()

    if filtered.empty:
        print("ERROR: No matching ward and category found.")
        return

    # Sort chronologically
    filtered["period"] = pd.to_datetime(
        filtered["period"],
        format="%Y-%m"
    )

    filtered = filtered.sort_values("period")

    results = []

    previous_actual = None
    previous_period = None

    for _, row in filtered.iterrows():

        current_period = row["period"].strftime("%Y-%m")
        current_actual = row["actual_spend"]

        # Handle NULL actual_spend
        if pd.isna(current_actual):
            reason = row["notes"]

            results.append({
                "period": current_period,
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "",
                "growth_type": "MoM",
                "formula": "NOT COMPUTED",
                "growth": "",
                "status": "FLAGGED: NULL actual_spend",
                "null_reason": reason
            })

            # A missing value cannot become a valid previous value
            previous_actual = None
            previous_period = current_period

            continue

        # First month has no previous month
        if previous_actual is None:
            results.append({
                "period": current_period,
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current_actual,
                "growth_type": "MoM",
                "formula": "N/A — first available period",
                "growth": "",
                "status": "NOT COMPUTED",
                "null_reason": ""
            })

        else:
            growth = ((current_actual - previous_actual) / previous_actual) * 100

            formula = (
                f"(({current_actual} - {previous_actual}) "
                f"/ {previous_actual}) * 100"
            )

            results.append({
                "period": current_period,
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current_actual,
                "growth_type": "MoM",
                "formula": formula,
                "growth": round(growth, 1),
                "status": "COMPUTED",
                "null_reason": ""
            })

        previous_actual = current_actual
        previous_period = current_period

    output_df = pd.DataFrame(results)

    output_df.to_csv(args.output, index=False,encoding="utf-8-sig")

    print(f"Done. Output written to {args.output}")
    print(f"Rows written: {len(output_df)}")


if __name__ == "__main__":
    main()