"""
UC-0C app.py — Budget Growth-Rate Calculator Agent.

Computes period-over-period spending growth per ward per category.
Implements the skills defined in skills.md (load_dataset, compute_growth)
and enforces the rules defined in agents.md.

Usage:
    python app.py \
        --input ../data/budget/ward_budget.csv \
        --ward "Ward 1 – Kasba" \
        --category "Roads & Pothole Repair" \
        --growth-type MoM \
        --output growth_output.csv
"""

import argparse
import sys
import os
import pandas as pd


# ---------------------------------------------------------------------------
# Skill 1: load_dataset
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = [
    "period", "ward", "category",
    "budgeted_amount", "actual_spend", "notes",
]


def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Reads the ward budget CSV, validates that all required columns are
    present, and reports the null count and which rows have null
    actual_spend values before returning the data.

    Raises:
        FileNotFoundError  – if the file does not exist.
        ValueError         – if required columns are missing or file is empty.
    """
    # --- File existence check ---
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")

    # --- Read CSV ---
    df = pd.read_csv(filepath)

    # --- Empty-file check ---
    if df.empty:
        raise ValueError("The input CSV contains no data rows.")

    # --- Column validation ---
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}. "
            f"Found columns: {', '.join(df.columns)}"
        )

    # --- Null actual_spend report ---
    null_mask = df["actual_spend"].isna()
    null_count = int(null_mask.sum())

    print("=" * 70)
    print("DATASET LOAD REPORT")
    print("=" * 70)
    print(f"  File          : {filepath}")
    print(f"  Total rows    : {len(df)}")
    print(f"  Null actual_spend rows: {null_count}")

    if null_count > 0:
        print()
        print("  ⚠  NULL ACTUAL_SPEND ROWS (will be excluded from growth):")
        print("  " + "-" * 66)
        for _, row in df[null_mask].iterrows():
            reason = row["notes"] if pd.notna(row["notes"]) else "No reason given"
            print(
                f"    Period: {row['period']}  |  "
                f"Ward: {row['ward']}  |  "
                f"Category: {row['category']}"
            )
            print(f"      Reason: {reason}")
        print("  " + "-" * 66)

    print("=" * 70)
    print()

    return df


# ---------------------------------------------------------------------------
# Skill 2: compute_growth
# ---------------------------------------------------------------------------
def compute_growth(
    df: pd.DataFrame,
    ward: str,
    category: str,
    growth_type: str,
) -> pd.DataFrame:
    """
    Filters the dataset for the given ward + category, then computes
    period-over-period growth (MoM or YoY).

    Returns a DataFrame with columns:
        period, actual_spend, previous_actual_spend,
        growth_formula, growth_percentage

    Raises:
        ValueError – if ward/category not found or growth_type invalid.
    """
    # --- Validate growth_type ---
    if growth_type not in ("MoM", "YoY"):
        print(
            f"ERROR: Invalid growth type '{growth_type}'. "
            "Please specify 'MoM' (month-over-month) or 'YoY' (year-over-year)."
        )
        sys.exit(1)

    # --- Validate ward ---
    available_wards = sorted(df["ward"].unique())
    if ward not in available_wards:
        raise ValueError(
            f"Ward '{ward}' not found in dataset.\n"
            f"Available wards: {', '.join(available_wards)}"
        )

    # --- Validate category ---
    available_categories = sorted(df["category"].unique())
    if category not in available_categories:
        raise ValueError(
            f"Category '{category}' not found in dataset.\n"
            f"Available categories: {', '.join(available_categories)}"
        )

    # --- Filter for requested ward + category ---
    subset = (
        df[(df["ward"] == ward) & (df["category"] == category)]
        .copy()
        .sort_values("period")
        .reset_index(drop=True)
    )

    # --- Flag null rows within this slice ---
    null_mask = subset["actual_spend"].isna()
    null_rows = subset[null_mask]

    if not null_rows.empty:
        print(f"⚠  Null actual_spend rows for {ward} / {category}:")
        for _, row in null_rows.iterrows():
            reason = row["notes"] if pd.notna(row["notes"]) else "No reason given"
            print(f"    Period {row['period']}: EXCLUDED — {reason}")
        print()

    # --- Check whether any valid data remains ---
    valid = subset[~null_mask].copy().reset_index(drop=True)
    if valid.empty:
        raise ValueError(
            f"All actual_spend values for {ward} / {category} are null. "
            "Cannot compute growth."
        )

    # --- Determine the shift (number of periods to look back) ---
    if growth_type == "MoM":
        shift = 1
        formula_label = "MoM"
    else:  # YoY
        shift = 12
        formula_label = "YoY"

    # --- Build result rows (using only non-null data) ---
    records = []
    for i, row in valid.iterrows():
        current_spend = row["actual_spend"]

        if i < shift:
            # Not enough prior data for this growth type
            records.append(
                {
                    "period": row["period"],
                    "ward": ward,
                    "category": category,
                    "actual_spend": current_spend,
                    "previous_actual_spend": "N/A",
                    "growth_formula": "N/A (no prior period)",
                    "growth_percentage": "N/A",
                }
            )
        else:
            prev_spend = valid.loc[i - shift, "actual_spend"]

            # If the prior-period value is also null after our filter this
            # shouldn't happen, but guard anyway.
            if pd.isna(prev_spend):
                records.append(
                    {
                        "period": row["period"],
                        "ward": ward,
                        "category": category,
                        "actual_spend": current_spend,
                        "previous_actual_spend": "N/A",
                        "growth_formula": "N/A (prior period null)",
                        "growth_percentage": "N/A",
                    }
                )
            elif prev_spend == 0:
                records.append(
                    {
                        "period": row["period"],
                        "ward": ward,
                        "category": category,
                        "actual_spend": current_spend,
                        "previous_actual_spend": prev_spend,
                        "growth_formula": "N/A (division by zero)",
                        "growth_percentage": "N/A",
                    }
                )
            else:
                growth_pct = round(
                    (current_spend - prev_spend) / prev_spend * 100, 1
                )
                formula_str = (
                    f"{formula_label} = ({current_spend} - {prev_spend}) "
                    f"/ {prev_spend} × 100"
                )
                records.append(
                    {
                        "period": row["period"],
                        "ward": ward,
                        "category": category,
                        "actual_spend": current_spend,
                        "previous_actual_spend": prev_spend,
                        "growth_formula": formula_str,
                        "growth_percentage": f"{growth_pct}%",
                    }
                )

    result = pd.DataFrame(records)
    return result


# ---------------------------------------------------------------------------
# Enforcement helpers
# ---------------------------------------------------------------------------
def _refuse_aggregation(ward: str | None, category: str | None) -> None:
    """Refuse if user tries to run without specifying both ward and category."""
    if not ward or not category:
        print(
            "ERROR: Cross-ward or cross-category aggregation is not allowed.\n"
            "Please specify both --ward and --category.\n"
            "This agent operates on a single ward + category at a time."
        )
        sys.exit(1)


def _refuse_missing_growth_type(growth_type: str | None) -> None:
    """Refuse if --growth-type was not supplied."""
    if not growth_type:
        print(
            "ERROR: --growth-type is required.\n"
            "Please specify 'MoM' (month-over-month) or 'YoY' (year-over-year).\n"
            "The agent will not guess or default silently."
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description=(
            "UC-0C Budget Growth-Rate Calculator — "
            "computes per-ward per-category spending growth."
        )
    )
    parser.add_argument(
        "--input",
        default="../data/budget/ward_budget.csv",
        help="Path to ward_budget.csv (default: ../data/budget/ward_budget.csv)",
    )
    parser.add_argument(
        "--ward",
        default=None,
        help="Ward name to compute growth for (required).",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Category to compute growth for (required).",
    )
    parser.add_argument(
        "--growth-type",
        default=None,
        dest="growth_type",
        help="Growth type: 'MoM' (month-over-month) or 'YoY' (year-over-year). Required.",
    )
    parser.add_argument(
        "--output",
        default="growth_output.csv",
        help="Output CSV filename (default: growth_output.csv)",
    )
    args = parser.parse_args()

    # --- Enforcement: refuse if ward or category missing ---
    _refuse_aggregation(args.ward, args.category)

    # --- Enforcement: refuse if growth type missing ---
    _refuse_missing_growth_type(args.growth_type)

    # --- Skill 1: load_dataset ---
    df = load_dataset(args.input)

    # --- Skill 2: compute_growth ---
    result = compute_growth(df, args.ward, args.category, args.growth_type)

    # --- Write output ---
    result.to_csv(args.output, index=False)
    print(f"✔  Output written to: {args.output}")
    print()
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
