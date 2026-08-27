"""
UC-0C app.py — Municipal Budget Growth Analyst
Built against agents.md (R.I.C.E) + skills.md contracts.

Run:
    python app.py \
        --input ../data/budget/ward_budget.csv \
        --ward "Ward 1 – Kasba" \
        --category "Roads & Pothole Repair" \
        --growth-type MoM \
        --output growth_output.csv
"""

import argparse
import sys
import pandas as pd

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ─────────────────────────────────────────────
# SKILL: load_dataset
# ─────────────────────────────────────────────

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Reads ward_budget.csv, validates columns, and prints a null report
    for every row where actual_spend is blank — before returning data.

    Raises:
        FileNotFoundError : if the file path does not exist
        ValueError        : if any required column is missing
    """
    # --- Load ---
    try:
        df = pd.read_csv(file_path, dtype={"period": str, "ward": str, "category": str, "notes": str})
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: '{file_path}'. Please check the path.")

    # --- Validate columns ---
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing column(s): {', '.join(sorted(missing))}. Cannot proceed.")

    # --- Null report (RULE 2: always printed before returning) ---
    null_rows = df[df["actual_spend"].isna()][["period", "ward", "category", "notes"]]
    null_count = len(null_rows)

    print(f"\n{'='*60}")
    print(f"DATASET LOADED: {len(df)} rows from '{file_path}'")
    print(f"NULL actual_spend rows found: {null_count}")

    if null_count > 0:
        print("\n⚠  The following rows have null actual_spend and will NOT be computed:")
        print(f"   {'Period':<10} {'Ward':<30} {'Category':<30} {'Reason'}")
        print(f"   {'-'*100}")
        for _, row in null_rows.iterrows():
            reason = row["notes"] if pd.notna(row["notes"]) else "No reason provided"
            print(f"   {row['period']:<10} {row['ward']:<30} {row['category']:<30} {reason}")
    else:
        print("   ✓ No null rows detected.")

    print(f"{'='*60}\n")

    return df


# ─────────────────────────────────────────────
# SKILL: compute_growth
# ─────────────────────────────────────────────

def compute_growth(
    data: pd.DataFrame,
    ward: str,
    category: str,
    growth_type: str,
) -> pd.DataFrame:
    """
    Computes MoM or YoY growth for a single ward + category.
    Returns a per-period DataFrame with formula_used and flag on every row.

    Raises:
        ValueError : if growth_type is invalid, ward not found, or category not found
    """
    # --- RULE 4: growth_type must be explicit ---
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"growth_type must be 'MoM' or 'YoY'. Received: '{growth_type}'. "
            "I will not pick one silently."
        )

    # --- RULE 1: ward and category must exist ---
    available_wards = data["ward"].unique().tolist()
    if ward not in available_wards:
        raise ValueError(
            f"Ward '{ward}' not found.\nAvailable wards: {available_wards}"
        )

    available_categories = data["category"].unique().tolist()
    if category not in available_categories:
        raise ValueError(
            f"Category '{category}' not found.\nAvailable categories: {available_categories}"
        )

    # --- Filter to exact ward + category slice ---
    slice_df = (
        data[(data["ward"] == ward) & (data["category"] == category)]
        .sort_values("period")
        .reset_index(drop=True)
    )

    results = []

    for i, row in slice_df.iterrows():
        period = row["period"]
        current = row["actual_spend"]
        flag = ""
        growth_pct = None
        formula_used = ""

        # --- RULE 2: null current value → NULL_FLAGGED, skip computation ---
        if pd.isna(current):
            flag = "NULL_FLAGGED"
            formula_used = "N/A — actual_spend is null"
            results.append({
                "period": period,
                "actual_spend": None,
                "growth_pct": None,
                "formula_used": formula_used,
                "flag": flag,
            })
            continue

        # --- Identify prior value based on growth_type ---
        if growth_type == "MoM":
            if i == 0:
                # First row — no prior month
                formula_used = "N/A — no prior month"
                flag = "BASE_NULL"
            else:
                prior = slice_df.loc[i - 1, "actual_spend"]
                prior_period = slice_df.loc[i - 1, "period"]
                if pd.isna(prior):
                    formula_used = f"N/A — prior month ({prior_period}) is null"
                    flag = "BASE_NULL"
                else:
                    growth_pct = round((current - prior) / prior * 100, 1)
                    formula_used = f"({current} - {prior}) / {prior} × 100"

        elif growth_type == "YoY":
            # Find same month in prior year
            current_year, current_month = period.split("-")
            prior_period_label = f"{int(current_year) - 1}-{current_month}"
            prior_rows = slice_df[slice_df["period"] == prior_period_label]

            if prior_rows.empty:
                formula_used = f"N/A — no data for prior year period ({prior_period_label})"
                flag = "BASE_NULL"
            else:
                prior = prior_rows.iloc[0]["actual_spend"]
                if pd.isna(prior):
                    formula_used = f"N/A — prior year period ({prior_period_label}) is null"
                    flag = "BASE_NULL"
                else:
                    growth_pct = round((current - prior) / prior * 100, 1)
                    formula_used = f"({current} - {prior}) / {prior} × 100"

        results.append({
            "period": period,
            "actual_spend": current,
            "growth_pct": growth_pct,
            "formula_used": formula_used,
            "flag": flag,
        })

    return pd.DataFrame(results, columns=["period", "actual_spend", "growth_pct", "formula_used", "flag"])


# ─────────────────────────────────────────────
# ENFORCEMENT GUARDS (agent-level, pre-skill)
# ─────────────────────────────────────────────

def enforce_args(args: argparse.Namespace):
    """
    Applies RULE 1 and RULE 4 at the CLI boundary before any skill is called.
    Exits with a clear refusal message rather than proceeding with bad inputs.
    """
    # RULE 1 — ward required
    if not args.ward or args.ward.strip().lower() == "all":
        print(
            "\n❌ REFUSED — Ward not specified or set to 'all'.\n"
            "   Aggregating across wards produces a misleading single number.\n"
            "   Please specify --ward with an exact ward name.\n"
        )
        sys.exit(1)

    # RULE 1 — category required
    if not args.category or args.category.strip().lower() == "all":
        print(
            "\n❌ REFUSED — Category not specified or set to 'all'.\n"
            "   Aggregating across categories produces a misleading single number.\n"
            "   Please specify --category with an exact category name.\n"
        )
        sys.exit(1)

    # RULE 4 — growth_type required
    if not args.growth_type:
        print(
            "\n❌ REFUSED — --growth-type is required.\n"
            "   Please specify MoM (month-over-month) or YoY (year-over-year).\n"
            "   I will not pick one silently.\n"
        )
        sys.exit(1)

    if args.growth_type not in ("MoM", "YoY"):
        print(
            f"\n❌ REFUSED — Invalid --growth-type '{args.growth_type}'.\n"
            "   Must be exactly 'MoM' or 'YoY'. I will not guess.\n"
        )
        sys.exit(1)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Per-ward per-category budget growth analyser."
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=False, help="Exact ward name")
    parser.add_argument("--category",   required=False, help="Exact category name")
    parser.add_argument("--growth-type", dest="growth_type", required=False,
                        help="MoM or YoY — required, never defaulted")
    parser.add_argument("--output",      required=True,  help="Output CSV filename")
    args = parser.parse_args()

    # ── Enforcement layer (before any skill) ──
    enforce_args(args)

    # ── SKILL 1: load_dataset ──
    try:
        df = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"\n❌ ERROR in load_dataset: {e}\n")
        sys.exit(1)

    # ── SKILL 2: compute_growth ──
    try:
        result = compute_growth(
            data=df,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
    except ValueError as e:
        print(f"\n❌ ERROR in compute_growth: {e}\n")
        sys.exit(1)

    # ── Print result table to stdout ──
    print(f"GROWTH REPORT — {args.ward} | {args.category} | {args.growth_type}\n")
    print(result.to_string(index=False))
    print()

    # ── Write output CSV ──
    result.to_csv(args.output, index=False)
    print(f"✓ Output written to: {args.output}\n")


if __name__ == "__main__":
    main()