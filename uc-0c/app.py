import pandas as pd
import argparse
import sys
import os

# -----------------------------
# Skill 1: load_dataset
# -----------------------------
def load_dataset(file_path):
    required_columns = [
        "period", "ward", "category",
        "budgeted_amount", "actual_spend", "notes"
    ]

    # File existence check
    if not os.path.exists(file_path):
        print("Error: Input file not found.")
        sys.exit(1)

    # Read CSV
    try:
        df = pd.read_csv(file_path)
    except Exception:
        print("Error: Unable to read dataset (corrupted or invalid format).")
        sys.exit(1)

    # Validate columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}")
        sys.exit(1)

    # Detect null rows
    null_rows = df[df["actual_spend"].isnull()]

    if not null_rows.empty:
        print(f"Null rows detected: {len(null_rows)}")
        print(null_rows[["period", "ward", "category", "notes"]])

    return df


# -----------------------------
# Skill 2: compute_growth
# -----------------------------
def compute_growth(df, ward, category, growth_type):
    # Enforce growth_type presence
    if not growth_type:
        print("Error: --growth-type not specified. Please provide (e.g., MoM).")
        sys.exit(1)

    # Only allow MoM (as per UC)
    if growth_type != "MoM":
        print("Error: Unsupported growth_type. Only 'MoM' is allowed.")
        sys.exit(1)

    # Validate ward & category existence
    if ward not in df["ward"].unique():
        print("Error: Ward not found in dataset.")
        sys.exit(1)

    if category not in df["category"].unique():
        print("Error: Category not found in dataset.")
        sys.exit(1)

    # Filter dataset (NO aggregation allowed)
    filtered = df[(df["ward"] == ward) & (df["category"] == category)].copy()

    if filtered.empty:
        print("Error: No data found for given ward and category.")
        sys.exit(1)

    # Sort by period
    filtered = filtered.sort_values("period")

    # Prepare previous values
    filtered["prev"] = filtered["actual_spend"].shift(1)

    growth_values = []
    formulas = []
    flags = []
    notes_col = []

    for _, row in filtered.iterrows():
        current = row["actual_spend"]
        prev = row["prev"]
        note = row["notes"]

        # Handle NULL actual_spend
        if pd.isnull(current):
            growth_values.append(None)
            formulas.append("NULL")
            flags.append(True)
            notes_col.append(note)
            continue

        # Handle missing previous value
        if pd.isnull(prev):
            growth_values.append(None)
            formulas.append("No previous data")
            flags.append(False)
            notes_col.append("")
            continue

        # Compute MoM growth
        growth = ((current - prev) / prev) * 100

        formula = f"({current} - {prev}) / {prev} * 100"

        growth_values.append(growth)
        formulas.append(formula)
        flags.append(False)
        notes_col.append("")

    # Build output table
    output_df = pd.DataFrame({
        "period": filtered["period"],
        "ward": filtered["ward"],
        "category": filtered["category"],
        "actual_spend": filtered["actual_spend"],
        "growth": growth_values,
        "formula": formulas,
        "null_flag": flags,
        "null_reason": notes_col
    })

    return output_df


# -----------------------------
# Main execution
# -----------------------------
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    # Load dataset
    df = load_dataset(args.input)

    # Compute growth
    result_df = compute_growth(
        df,
        args.ward,
        args.category,
        args.growth_type
    )

    # Enforce output is NOT aggregated
    if len(result_df) <= 1:
        print("Error: Output appears aggregated. Refusing to proceed.")
        sys.exit(1)

    # Save output
    try:
        result_df.to_csv(args.output, index=False)
        print(f"Output saved to {args.output}")
    except Exception:
        print("Error: Failed to write output file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
