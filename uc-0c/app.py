"""
UC-0C app.py — Budget Growth Analyser
Implements agents.md (RICE) + skills.md (load_dataset, compute_growth).
"""
import argparse
import sys
import pandas as pd

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str) -> tuple[pd.DataFrame, list[dict]]:
    """
    Read ward_budget.csv, validate schema, surface every null actual_spend row
    before returning.  Raises ValueError on missing columns or empty file.
    """
    df = pd.read_csv(file_path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("CSV loaded but contains zero data rows.")

    null_mask = df["actual_spend"].isna()
    null_report = (
        df.loc[null_mask, ["period", "ward", "category", "notes"]]
        .to_dict(orient="records")
    )

    return df, null_report


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(
    df: pd.DataFrame,
    ward: str,
    category: str,
    growth_type: str,
) -> pd.DataFrame:
    """
    Compute per-period MoM or YoY growth for a single ward+category slice.
    Null rows are marked SKIPPED — never filled or interpolated.
    Every row carries the exact formula string used.
    Refuses (raises ValueError) if growth_type is absent or unrecognised.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            "growth_type must be 'MoM' or 'YoY' — please specify explicitly."
        )

    slice_df = df[(df["ward"] == ward) & (df["category"] == category)].copy()

    if slice_df.empty:
        raise ValueError(
            f"No data found for ward='{ward}' / category='{category}'. "
            "Check spelling against the CSV."
        )

    slice_df = slice_df.sort_values("period").reset_index(drop=True)

    rows = []
    for i, row in slice_df.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        note = row["notes"] if pd.notna(row["notes"]) and str(row["notes"]).strip() else ""

        if pd.isna(actual):
            rows.append({
                "period": period,
                "actual_spend": None,
                "formula": f"SKIPPED — null actual_spend ({note})" if note else "SKIPPED — null actual_spend",
                "growth_rate": None,
                "flag": "NULL",
            })
            continue

        # Find the reference period value
        prev_actual = None
        if growth_type == "MoM":
            prev_rows = slice_df[slice_df["period"] < period].tail(1)
            if not prev_rows.empty:
                prev_val = prev_rows.iloc[0]["actual_spend"]
                prev_period = prev_rows.iloc[0]["period"]
                if pd.notna(prev_val):
                    prev_actual = (prev_val, prev_period)
        else:  # YoY
            # Same month, previous year
            year = int(period[:4])
            month = period[5:]
            prev_period = f"{year - 1}-{month}"
            prev_rows = slice_df[slice_df["period"] == prev_period]
            if not prev_rows.empty:
                prev_val = prev_rows.iloc[0]["actual_spend"]
                if pd.notna(prev_val):
                    prev_actual = (prev_val, prev_period)

        if prev_actual is None:
            rows.append({
                "period": period,
                "actual_spend": round(actual, 2),
                "formula": "N/A — no prior period available",
                "growth_rate": None,
                "flag": "FIRST_PERIOD",
            })
        else:
            ref_val, ref_period = prev_actual
            growth = (actual - ref_val) / ref_val * 100
            formula = f"({actual:.1f} - {ref_val:.1f}) / {ref_val:.1f} * 100"
            rows.append({
                "period": period,
                "actual_spend": round(actual, 2),
                "formula": formula,
                "growth_rate": round(growth, 1),
                "flag": "",
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="UC-0C: Compute MoM/YoY budget growth per ward per category."
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name (exact match)")
    parser.add_argument("--category",    required=True,  help="Category name (exact match)")
    parser.add_argument("--growth-type", required=False, dest="growth_type",
                        choices=["MoM", "YoY"],
                        help="MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output",      required=True,  help="Output CSV file name")
    return parser.parse_args()


def main():
    args = parse_args()

    # Enforcement: refuse if growth-type not supplied
    if not args.growth_type:
        print(
            "ERROR: --growth-type is required. "
            "Please specify 'MoM' (month-over-month) or 'YoY' (year-over-year).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Skill: load_dataset
    print(f"Loading dataset from: {args.input}")
    try:
        df, null_report = load_dataset(args.input)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(df)} rows.")

    # Enforcement: surface all null rows BEFORE computing
    if null_report:
        print(f"\n{'-'*60}")
        print(f"WARNING: {len(null_report)} null actual_spend row(s) found in the full dataset:")
        for r in null_report:
            note = r.get("notes", "")
            note_str = f" | reason: {note}" if pd.notna(note) and str(note).strip() else ""
            print(f"  - {r['period']} / {r['ward']} / {r['category']}{note_str}")
        print(f"{'-'*60}\n")
    else:
        print("No null rows found in the dataset.")

    # Enforcement: refuse cross-ward / cross-category aggregation
    if args.ward.lower() in ("all", "*") or args.category.lower() in ("all", "*"):
        print(
            "ERROR: Cross-ward or cross-category aggregation is not allowed. "
            "Provide a specific --ward and --category.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Skill: compute_growth
    print(f"Computing {args.growth_type} growth for: {args.ward} / {args.category}\n")
    try:
        result = compute_growth(df, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Display to stdout
    print(result.to_string(index=False))
    print()

    # Write output CSV
    result.to_csv(args.output, index=False)
    print(f"Output written to: {args.output}")


if __name__ == "__main__":
    main()
