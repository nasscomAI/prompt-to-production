
"""
UC-0C — Budget Growth Analysis

Enforces:
- Correct aggregation level (per ward, per category, per period)
- Explicit null handling
- Explicit growth formula selection
- Refusal on ambiguity or unsafe aggregation
"""

import argparse
import sys
from pathlib import Path
import pandas as pd


# =========================
# Skill: load_dataset
# =========================
def load_dataset(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    required_columns = {
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


# =========================
# Skill: compute_growth
# =========================
def compute_growth(
    df: pd.DataFrame, ward: str, category: str, growth_type: str
) -> pd.DataFrame:
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError(f"Invalid growth type: {growth_type}")

    scoped = df[(df["ward"] == ward) & (df["category"] == category)]

    if scoped.empty:
        raise ValueError("No data found for given ward and category")

    scoped = scoped.sort_values("period")

    results = []

    for idx, row in scoped.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        note = row["notes"]

        if pd.isna(actual):
            results.append(
                {
                    "period": period,
                    "actual_spend": None,
                    "growth": None,
                    "formula": None,
                    "status": f"NULL actual_spend — {note}",
                }
            )
            continue

        if growth_type == "MoM":
            prev = scoped.loc[
                scoped["period"] < period, "actual_spend"
            ].dropna()
            base = prev.iloc[-1] if not prev.empty else None
            formula = "(current - previous) / previous"
        else:  # YoY
            year_ago = period[:4] + "-" + period[5:]
            prev = scoped.loc[
                scoped["period"] == year_ago, "actual_spend"
            ].dropna()
            base = prev.iloc[0] if not prev.empty else None
            formula = "(current - year_ago) / year_ago"

        if base is None or base == 0:
            results.append(
                {
                    "period": period,
                    "actual_spend": actual,
                    "growth": None,
                    "formula": formula,
                    "status": "Growth not computable (missing base period)",
                }
            )
        else:
            growth = (actual - base) / base
            results.append(
                {
                    "period": period,
                    "actual_spend": actual,
                    "growth": round(growth * 100, 2),
                    "formula": formula,
                    "status": "OK",
                }
            )

    return pd.DataFrame(results)


# =========================
# Skill: validate_output
# =========================
def validate_output(df: pd.DataFrame, ward: str, category: str):
    if df.empty:
        raise ValueError("Output is empty")

    if not all(df["period"].notna()):
        raise ValueError("Missing period values in output")

    if df["growth"].count() == 1:
        raise ValueError(
            "Detected single aggregated number — per-period table required"
        )


# =========================
# Main
# =========================
def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analysis")

    parser.add_argument("--input", required=True, help="CSV input file")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument(
        "--growth-type", required=True, choices=["MoM", "YoY"]
    )
    parser.add_argument("--output", required=True, help="Output CSV file")

    args = parser.parse_args()

    try:
        df = load_dataset(Path(args.input))
        result = compute_growth(
            df, args.ward, args.category, args.growth_type
        )
        validate_output(result, args.ward, args.category)
        result.to_csv(args.output, index=False)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
