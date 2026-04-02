import argparse
import pandas as pd
import sys
import os


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


# ---------------------------
# Skill 1: load_dataset
# ---------------------------
def load_dataset(file_path):
    # File validation
    if not os.path.exists(file_path):
        fail("File path is invalid or file cannot be read")

    try:
        df = pd.read_csv(file_path)
    except Exception:
        fail("File cannot be read")

    # Column validation
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        fail(f"Missing required columns: {missing_cols}")

    # Period format validation
    try:
        pd.to_datetime(df["period"], format="%Y-%m", errors="raise")
    except Exception:
        fail("Invalid period format, must be YYYY-MM")

    # Structure validation (basic sanity)
    if df.shape[0] == 0:
        fail("Dataset is empty")

    # Null detection (critical enforcement)
    null_rows = df[df["actual_spend"].isna()]

    null_details = []
    for _, row in null_rows.iterrows():
        null_details.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "notes": row["notes"]
        })

    print(f"Loaded dataset with {len(df)} rows")
    print(f"Detected {len(null_details)} null actual_spend rows")

    for r in null_details:
        print(f"NULL -> {r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")

    return df, null_details


# ---------------------------
# Skill 2: compute_growth
# ---------------------------
def compute_growth(df, ward, category, growth_type):
    # Validate inputs
    if not ward or ward not in df["ward"].unique():
        fail("Invalid or missing ward")

    if not category or category not in df["category"].unique():
        fail("Invalid or missing category")

    if not growth_type:
        fail("Missing --growth-type (refuse to assume)")

    if growth_type != "MoM":
        fail("Unsupported growth_type (only MoM supported explicitly)")

    # Enforce no aggregation
    filtered = df[(df["ward"] == ward) & (df["category"] == category)]

    if filtered.empty:
        fail("No data found for given ward and category")

    # Sort by period
    filtered = filtered.sort_values("period").reset_index(drop=True)

    results = []

    for i, row in filtered.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        note = row["notes"]

        # Null handling
        if pd.isna(actual):
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": None,
                "growth_value": None,
                "formula_used": None,
                "null_flag": True,
                "null_reason": note
            })
            continue

        # First row (no previous)
        if i == 0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "growth_value": None,
                "formula_used": "No previous period",
                "null_flag": False,
                "null_reason": None
            })
            continue

        prev = filtered.loc[i - 1, "actual_spend"]

        # Previous null → cannot compute
        if pd.isna(prev):
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "growth_value": None,
                "formula_used": None,
                "null_flag": True,
                "null_reason": "Previous period actual_spend is null"
            })
            continue

        # Compute MoM growth
        growth = ((actual - prev) / prev) * 100

        formula = f"(({actual} - {prev}) / {prev}) * 100"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual,
            "growth_value": round(growth, 1),
            "formula_used": formula,
            "null_flag": False,
            "null_reason": None
        })

    result_df = pd.DataFrame(results)

    # Validate output is not aggregated
    if len(result_df) <= 1:
        fail("Output appears aggregated — refusing")

    # Ensure formula exists
    if result_df["formula_used"].isna().any():
        # allowed only for null rows
        invalid = result_df[
            (result_df["null_flag"] == False) &
            (result_df["formula_used"].isna())
        ]
        if not invalid.empty:
            fail("Missing formula in output rows")

    return result_df


# ---------------------------
# Reference validation
# ---------------------------
def validate_reference(df):
    checks = [
        ("Ward 1 – Kasba", "Roads & Pothole Repair", "2024-07", 19.7, 33.1),
        ("Ward 1 – Kasba", "Roads & Pothole Repair", "2024-10", 13.1, -34.8),
    ]

    for ward, category, period, actual_ref, growth_ref in checks:
        row = df[
            (df["ward"] == ward) &
            (df["category"] == category) &
            (df["period"] == period)
        ]

        if not row.empty:
            r = row.iloc[0]

            if r["actual_spend"] != actual_ref:
                fail(f"Reference mismatch for {period} actual_spend")

            if r["growth_value"] is not None:
                if round(r["growth_value"], 1) != growth_ref:
                    fail(f"Reference mismatch for {period} growth_value")


# ---------------------------
# Main
# ---------------------------
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if not args.growth_type:
        fail("Missing --growth-type (refuse to assume)")

    # Load dataset
    df, nulls = load_dataset(args.input)

    # Compute growth
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)

    # Validate references (strict enforcement)
    validate_reference(result_df)

    # Save output
    output_path = args.output
    result_df.to_csv(output_path, index=False)

    print(f"Output written to {output_path}")


if __name__ == "__main__":
    main()