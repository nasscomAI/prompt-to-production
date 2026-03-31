import argparse
import os
import pandas as pd


# ---------------- SKILL 1 ----------------
def load_dataset(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    df = pd.read_csv(file_path)

    required_cols = [
        "period", "ward", "category",
        "budgeted_amount", "actual_spend", "notes"
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    if df.empty:
        raise ValueError("Dataset is empty.")

    # Identify null rows
    null_rows = df[df["actual_spend"].isna()]

    null_report = []
    for _, row in null_rows.iterrows():
        null_report.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "reason": row["notes"]
        })

    return df, null_report


# ---------------- SKILL 2 ----------------
def compute_growth(df, ward, category, growth_type):
    if growth_type is None:
        raise ValueError("Missing --growth-type. Refusing to assume.")

    if growth_type not in ["MoM", "YoY"]:
        raise ValueError("Invalid growth type. Must be MoM or YoY.")

    # Filter strictly (NO aggregation allowed)
    filtered = df[(df["ward"] == ward) & (df["category"] == category)]

    if filtered.empty:
        raise ValueError("No data found for given ward and category.")

    # Sort by period
    filtered = filtered.sort_values("period").reset_index(drop=True)

    results = []

    for i in range(len(filtered)):
        row = filtered.iloc[i]
        curr_val = row["actual_spend"]
        period = row["period"]

        # Determine comparison index
        if growth_type == "MoM":
            prev_index = i - 1
        else:  # YoY
            prev_index = i - 12

        if prev_index < 0:
            results.append({
                "period": period,
                "actual_spend": curr_val,
                "growth": "N/A",
                "formula": "Insufficient data",
                "note": "Not computed"
            })
            continue

        prev_val = filtered.iloc[prev_index]["actual_spend"]

        # Null handling (STRICT)
        if pd.isna(curr_val) or pd.isna(prev_val):
            results.append({
                "period": period,
                "actual_spend": curr_val,
                "growth": "NULL",
                "formula": "Not computed due to null",
                "note": "Null encountered"
            })
            continue

        # Compute growth
        growth = ((curr_val - prev_val) / prev_val) * 100

        formula = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"

        results.append({
            "period": period,
            "actual_spend": curr_val,
            "growth": round(growth, 2),
            "formula": formula,
            "note": ""
        })

    return pd.DataFrame(results)


# ---------------- MAIN ----------------
def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        # Load dataset
        df, null_report = load_dataset(args.input)

        # Print null report (enforcement)
        if null_report:
            print("⚠️ Null rows detected:")
            for r in null_report:
                print(r)

        # Compute growth
        result_df = compute_growth(
            df,
            args.ward,
            args.category,
            args.growth_type
        )

        # Save output
        result_df.to_csv(args.output, index=False)

        print("✅ Growth output generated successfully.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()