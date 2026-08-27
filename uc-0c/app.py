"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import pandas as pd


# -----------------------------
# Skill 1: load_dataset
# -----------------------------
def load_dataset(file_path):
    required_columns = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    ]

    # Validate file path
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: File not found at {file_path}")

    df = pd.read_csv(file_path)

    # Validate columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Error: Missing required columns: {missing_cols}")

    # Identify null rows in actual_spend
    null_rows = df[df["actual_spend"].isna()].copy()

    null_info = []
    for _, row in null_rows.iterrows():
        null_info.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "reason": row["notes"]
        })

    print(f"Loaded dataset with {len(df)} rows")
    print(f"Found {len(null_rows)} rows with null actual_spend")

    if len(null_info) > 0:
        print("Null rows (flagged):")
        for r in null_info:
            print(r)

    return {
        "data": df,
        "null_rows": null_info,
        "columns_valid": True
    }


# -----------------------------
# Skill 2: compute_growth
# -----------------------------
def compute_growth(dataset, ward, category, growth_type):
    if not growth_type:
        raise ValueError("Error: --growth-type not specified. Please provide MoM or YoY.")

    if growth_type not in ["MoM", "YoY"]:
        raise ValueError("Error: growth_type must be 'MoM' or 'YoY'")

    df = dataset["data"]

    # Filter strictly per ward + category (NO aggregation)
    filtered = df[(df["ward"] == ward) & (df["category"] == category)].copy()

    if filtered.empty:
        raise ValueError("Error: No data found for given ward and category")

    # Sort by period
    filtered = filtered.sort_values("period")

    results = []

    for i in range(len(filtered)):
        row = filtered.iloc[i]

        period = row["period"]
        actual = row["actual_spend"]

        # Handle null actual_spend
        if pd.isna(actual):
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": "NULL",
                "growth_value": "NULL",
                "formula": f"NULL (Reason: {row['notes']})"
            })
            continue

        # Determine previous period index
        prev_idx = None
        if growth_type == "MoM":
            prev_idx = i - 1
        elif growth_type == "YoY":
            prev_idx = i - 12

        if prev_idx is None or prev_idx < 0:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": actual,
                "growth_value": "NA",
                "formula": "No previous period available"
            })
            continue

        prev_row = filtered.iloc[prev_idx]
        prev_actual = prev_row["actual_spend"]

        # Handle null previous value
        if pd.isna(prev_actual):
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": actual,
                "growth_value": "NULL",
                "formula": f"NULL (Previous value missing: {prev_row['notes']})"
            })
            continue

        # Compute growth
        growth = ((actual - prev_actual) / prev_actual) * 100

        formula = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"

        results.append({
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": actual,
            "growth_value": round(growth, 2),
            "formula": formula
        })

    return pd.DataFrame(results)


# -----------------------------
# Main Application
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Budget Growth Computation Assistant")

    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=False, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV file name")

    args = parser.parse_args()

    # Enforcement: growth-type must be provided
    if not args.growth_type:
        raise ValueError("Refusal: --growth-type not specified. Please provide MoM or YoY.")

    # Load dataset
    dataset = load_dataset(args.input)

    # Compute growth
    result_df = compute_growth(
        dataset,
        args.ward,
        args.category,
        args.growth_type
    )

    # Ensure output directory
    output_path = os.path.join("uc-0c", args.output)
    os.makedirs("uc-0c", exist_ok=True)

    # Save output
    result_df.to_csv(output_path, index=False)

    print(f"\nOutput saved to: {output_path}")


if __name__ == "__main__":
    main()