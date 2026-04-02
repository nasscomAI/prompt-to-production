"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import pandas as pd
import argparse
import os


# -----------------------------
# Skill 1: load_dataset
# -----------------------------
def load_dataset(file_path):
    df = pd.read_csv(file_path)

    required_cols = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    ]

    # Validate columns
    for col in required_cols:
        if col not in df.columns:
            raise Exception(f"[FAIL] Missing required column: {col}")

    # Find null rows
    null_rows = df[df["actual_spend"].isnull()]

    print(f"[INFO] Total null rows in actual_spend: {len(null_rows)}")

    if len(null_rows) > 0:
        print("[INFO] Null rows (must be flagged):")
        print(null_rows[["period", "ward", "category", "notes"]])

    return df


# -----------------------------
# Skill 2: compute_growth
# -----------------------------
def compute_growth(df, ward, category, growth_type):
    # Enforcement: growth type must be provided
    if not growth_type:
        raise Exception("[FAIL] growth_type not specified — refusing to assume")

    if growth_type != "MoM":
        raise Exception("[FAIL] Only MoM supported as per requirement")

    # Filter strictly
    filtered = df[(df["ward"] == ward) & (df["category"] == category)]

    if filtered.empty:
        raise Exception("[FAIL] No data found for given ward and category")

    # Sort by period
    filtered = filtered.sort_values(by="period").reset_index(drop=True)

    output_rows = []

    for i in range(len(filtered)):
        row = filtered.iloc[i]

        current_value = row["actual_spend"]

        # Handle NULL rows
        if pd.isnull(current_value):
            output_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "NULL",
                "growth": "NOT COMPUTED",
                "formula": "N/A",
                "notes": row["notes"]
            })
            continue

        # First row → no previous value
        if i == 0:
            output_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current_value,
                "growth": "N/A",
                "formula": "No previous month",
                "notes": row["notes"]
            })
            continue

        prev_value = filtered.iloc[i - 1]["actual_spend"]

        # If previous is NULL → cannot compute
        if pd.isnull(prev_value):
            output_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current_value,
                "growth": "NOT COMPUTED",
                "formula": "Previous month NULL",
                "notes": row["notes"]
            })
            continue

        # Compute MoM growth
        growth = ((current_value - prev_value) / prev_value) * 100

        formula = f"(({current_value} - {prev_value}) / {prev_value}) * 100"

        output_rows.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": round(current_value, 2),
            "growth": f"{round(growth, 2)}%",
            "formula": formula,
            "notes": row["notes"]
        })

    return pd.DataFrame(output_rows)


# -----------------------------
# MAIN
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

    # Ensure output folder exists
    output_dir = os.path.dirname(args.output)
    if output_dir != "":
        os.makedirs(output_dir, exist_ok=True)

    # Save output
    result_df.to_csv(args.output, index=False)

    print(f"[SUCCESS] Growth output saved to {args.output}")


if __name__ == "__main__":
    main()