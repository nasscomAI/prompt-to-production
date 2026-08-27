"""UC-0C growth calculator.

This CLI app is intentionally strict:
- it requires a single ward + single category scope,
- it refuses to guess the growth type,
- it flags null actual_spend rows before computing,
- and it writes a per-period table with the formula used for each row.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def fail(message: str) -> None:
    print(f"REFUSE: {message}")
    sys.exit(1)


def load_dataset(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        fail(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        fail(f"Input file is missing required columns: {', '.join(missing)}")

    return df


def validate_args(args: argparse.Namespace) -> None:
    if not args.growth_type:
        fail("Missing --growth-type. Please specify MoM or YoY and do not guess.")

    growth_type = args.growth_type.strip().upper()
    if growth_type not in {"MOM", "YOY"}:
        fail("Unsupported --growth-type. Use MoM or YoY only.")

    if not args.ward or not args.category:
        fail("Please specify exactly one --ward and one --category. Do not aggregate across wards or categories.")

    if args.ward.strip().lower() in {"all", "all wards", "all-ward", "multiple"}:
        fail("All-ward aggregation is not allowed. Please provide one ward only.")

    if args.category.strip().lower() in {"all", "all categories", "all-category", "multiple"}:
        fail("All-category aggregation is not allowed. Please provide one category only.")


def compute_growth(df: pd.DataFrame, ward: str, category: str, growth_type: str) -> pd.DataFrame:
    subset = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    subset = subset.sort_values("period").reset_index(drop=True)

    if subset.empty:
        fail(f"No data found for ward '{ward}' and category '{category}'.")

    subset["actual_spend"] = pd.to_numeric(subset["actual_spend"], errors="coerce")

    flagged = subset[subset["actual_spend"].isna()].copy()
    if not flagged.empty:
        print("FLAGGED NULL ROWS BEFORE COMPUTING:")
        for _, row in flagged.iterrows():
            print(f"- {row['period']} | {row['ward']} | {row['category']} | notes: {row['notes']}")

    output_rows = []
    for idx, row in subset.iterrows():
        period = row["period"]
        current_value = row["actual_spend"]
        status = "ok"
        formula = "n/a"
        growth_value = "n/a"

        if pd.isna(current_value):
            status = "FLAGGED_NULL"
            formula = "n/a"
            growth_value = "n/a"
        else:
            previous = subset.loc[idx - 1, "actual_spend"] if idx > 0 else None
            if idx == 0:
                status = "baseline"
                formula = "baseline period; no previous month available"
                growth_value = "n/a"
            elif pd.isna(previous):
                status = "FLAGGED_NULL"
                formula = "n/a"
                growth_value = "n/a"
            else:
                if growth_type == "MOM":
                    growth_value = round(((current_value - previous) / previous) * 100, 2)
                    formula = f"(({current_value} - {previous}) / {previous}) * 100"
                else:
                    prior_year_same_month = subset.loc[idx - 12, "actual_spend"] if idx >= 12 else None
                    if pd.isna(prior_year_same_month):
                        status = "FLAGGED_NULL"
                        formula = "n/a"
                        growth_value = "n/a"
                    else:
                        growth_value = round(((current_value - prior_year_same_month) / prior_year_same_month) * 100, 2)
                        formula = f"(({current_value} - {prior_year_same_month}) / {prior_year_same_month}) * 100"

        output_rows.append(
            {
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current_value,
                "growth_type": growth_type,
                "growth_percent": growth_value,
                "formula": formula,
                "status": status,
                "notes": row["notes"],
            }
        )

    return pd.DataFrame(output_rows)


def write_output(result_df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_path, index=False)
    print(f"Wrote growth table to {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute per-ward per-category growth from the budget CSV.")
    parser.add_argument("--input", required=True, help="Path to the budget CSV file")
    parser.add_argument("--ward", required=True, help="Exact ward name; do not pass all wards")
    parser.add_argument("--category", required=True, help="Exact category name; do not pass all categories")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY; must be provided explicitly")
    parser.add_argument("--output", required=True, help="Output CSV path")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    validate_args(args)
    df = load_dataset(Path(args.input))
    growth_type = args.growth_type.strip().upper()
    result_df = compute_growth(df, args.ward, args.category, growth_type)
    write_output(result_df, Path(args.output))


if __name__ == "__main__":
    main()
