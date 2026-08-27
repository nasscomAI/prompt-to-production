"""
UC-0C — Number That Looks Right
Budget growth analysis agent: per-ward, per-category growth calculator.

Enforcement rules (from agents.md):
  1. Never aggregate across wards or categories — refuse if asked.
  2. Flag every null actual_spend row before computing growth.
  3. Report null reason from the notes column for every flagged null row.
  4. Do not compute growth for null actual_spend rows.
  5. Show the formula used in every output row alongside the result.
  6. If --growth-type is not specified, refuse and ask — never guess.
  7. Output must be a per-ward, per-category table — never a single aggregated number.
  8. Validate required columns before computation.
  9. Report null count and identify null rows during dataset validation.
 10. Compute growth only for the requested ward and category.
 11. Do not silently handle, fill, replace, or ignore null values.
 12. Do not assume a growth formula not explicitly requested.
"""

import argparse
import sys
import os
import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

VALID_GROWTH_TYPES = {"MoM", "YoY"}

KNOWN_WARDS = {
    "Ward 1 – Kasba",
    "Ward 2 – Shivajinagar",
    "Ward 3 – Kothrud",
    "Ward 4 – Warje",
    "Ward 5 – Hadapsar",
}

KNOWN_CATEGORIES = {
    "Roads & Pothole Repair",
    "Drainage & Flooding",
    "Waste Management",
    "Parks & Greening",
    "Streetlight Maintenance",
}


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class ValidationError(Exception):
    """Raised when dataset validation fails."""


class EnforcementError(Exception):
    """Raised when an enforcement rule is violated."""


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str) -> dict:
    """
    Reads the ward budget CSV, validates required columns are present,
    and reports null count and exact row identifiers for any null
    actual_spend values before returning the dataset.

    Parameters
    ----------
    file_path : str
        Path to the input CSV file.

    Returns
    -------
    dict with keys:
        - dataframe   : pd.DataFrame of all validated rows
        - null_count  : int
        - null_rows   : list of dicts (period, ward, category, notes)

    Raises
    ------
    FileNotFoundError   — if the file does not exist at the given path.
    ValidationError     — if required columns are missing or types are wrong.
    EnforcementError    — if the path is empty/None (ambiguous).
    """

    # --- ambiguous_path guard ---
    if not file_path or not file_path.strip():
        raise EnforcementError(
            "REFUSED: File path is empty or ambiguous. "
            "Please supply an explicit, unambiguous path to the CSV file."
        )

    # --- missing_file guard ---
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"REFUSED: Input file not found at path: '{file_path}'. "
            "Verify the path and try again."
        )

    # --- read CSV ---
    try:
        df = pd.read_csv(file_path, dtype=str)  # read all as str first for safe validation
    except Exception as exc:
        raise ValidationError(f"Failed to read CSV at '{file_path}': {exc}") from exc

    # --- missing_columns guard ---
    actual_cols = set(df.columns.str.strip().str.lower())
    # normalise column names to lowercase for comparison
    df.columns = df.columns.str.strip()
    present_cols = set(df.columns.str.lower())
    missing = {c for c in REQUIRED_COLUMNS if c not in present_cols}
    if missing:
        raise ValidationError(
            f"REFUSED: The following required columns are absent from the dataset: "
            f"{sorted(missing)}. Cannot proceed with partial data."
        )

    # Normalise column names to expected casing (match REQUIRED_COLUMNS exactly)
    col_map = {c.lower(): c for c in REQUIRED_COLUMNS}
    df.rename(columns={c: col_map[c.lower()] for c in df.columns if c.lower() in col_map},
              inplace=True)

    # --- wrong_column_types guard ---
    # period must match YYYY-MM
    invalid_periods = df[~df["period"].str.match(r"^\d{4}-\d{2}$", na=False)]
    if not invalid_periods.empty:
        raise ValidationError(
            f"REFUSED: Column 'period' contains {len(invalid_periods)} rows with values "
            f"that do not match the expected YYYY-MM format. "
            f"First offending value: '{invalid_periods['period'].iloc[0]}'. Halting."
        )

    # budgeted_amount must be numeric (non-null by schema)
    try:
        df["budgeted_amount"] = pd.to_numeric(df["budgeted_amount"], errors="raise")
    except Exception:
        bad = df[pd.to_numeric(df["budgeted_amount"], errors="coerce").isna()]
        raise ValidationError(
            f"REFUSED: Column 'budgeted_amount' contains non-numeric values. "
            f"Observed type anomaly at rows: {bad.index.tolist()[:5]}. Halting."
        )

    # actual_spend: convert to numeric; blank → NaN (deliberate nulls)
    df["actual_spend"] = pd.to_numeric(df["actual_spend"], errors="coerce")

    # --- null reporting (enforcement rules 2, 9) ---
    null_mask = df["actual_spend"].isna()
    null_count = int(null_mask.sum())
    null_rows = []
    for _, row in df[null_mask].iterrows():
        null_rows.append({
            "period":   row["period"],
            "ward":     row["ward"],
            "category": row["category"],
            "notes":    row["notes"] if pd.notna(row["notes"]) else "(no reason recorded)",
        })

    print(f"\n[load_dataset] Dataset loaded successfully.")
    print(f"  Rows total  : {len(df)}")
    print(f"  Null actual_spend count: {null_count}")
    if null_count == 0:
        print("  No null actual_spend rows found.")
    else:
        print("  Null rows (must be flagged — growth will NOT be computed for these):")
        for nr in null_rows:
            print(f"    • {nr['period']} | {nr['ward']} | {nr['category']} | reason: {nr['notes']}")
    print()

    return {
        "dataframe":  df,
        "null_count": null_count,
        "null_rows":  null_rows,
    }


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(
    dataset_result: dict,
    ward: str,
    category: str,
    growth_type: str,
) -> pd.DataFrame:
    """
    Computes per-period growth for the specified ward and category.

    Returns a DataFrame with columns:
        period, ward, category, actual_spend, growth_value, formula,
        null_flag, null_reason

    Enforcement rules enforced here:
        - Refuses if growth_type is missing (rule 6, 12).
        - Refuses cross-ward / cross-category aggregation (rule 1, 7).
        - Flags null rows; does not compute growth for them (rules 2–4, 11).
        - Shows formula in every output row (rule 5).
        - Validates ward and category against known values (unrecognised guard).

    Parameters
    ----------
    dataset_result : dict   Output of load_dataset().
    ward           : str    Exact ward name.
    category       : str    Exact category name.
    growth_type    : str    "MoM" or "YoY".

    Returns
    -------
    pd.DataFrame
    """

    # --- missing_growth_type guard (enforcement rule 6) ---
    if growth_type is None or growth_type.strip() == "":
        raise EnforcementError(
            "REFUSED: --growth-type was not specified. "
            "Please explicitly provide 'MoM' (month-over-month) or 'YoY' (year-over-year). "
            "This agent will never guess or default the growth formula."
        )

    if growth_type not in VALID_GROWTH_TYPES:
        raise EnforcementError(
            f"REFUSED: Unrecognised growth_type '{growth_type}'. "
            f"Valid options are: {sorted(VALID_GROWTH_TYPES)}. "
            "Please specify one explicitly."
        )

    # --- aggregation guard: ward == ALL or category == ALL (enforcement rule 1) ---
    if ward.strip().upper() in {"ALL", "*", ""} or category.strip().upper() in {"ALL", "*", ""}:
        raise EnforcementError(
            "REFUSED: Cross-ward or cross-category aggregation is not permitted. "
            "You must specify an explicit single ward and a single category. "
            "Aggregation across wards or categories requires explicit operator instruction."
        )

    # --- unrecognised_ward_or_category guard ---
    if ward not in KNOWN_WARDS:
        raise EnforcementError(
            f"REFUSED: Ward '{ward}' is not recognised. "
            f"Valid wards are:\n  " + "\n  ".join(sorted(KNOWN_WARDS))
        )
    if category not in KNOWN_CATEGORIES:
        raise EnforcementError(
            f"REFUSED: Category '{category}' is not recognised. "
            f"Valid categories are:\n  " + "\n  ".join(sorted(KNOWN_CATEGORIES))
        )

    df = dataset_result["dataframe"]

    # --- filter to requested ward + category only (enforcement rule 10) ---
    mask = (df["ward"] == ward) & (df["category"] == category)
    subset = df[mask].copy().sort_values("period").reset_index(drop=True)

    if subset.empty:
        raise ValidationError(
            f"No rows found for ward='{ward}', category='{category}'. "
            "Check that the values match the dataset exactly."
        )

    # --- build output rows ---
    output_rows = []

    for i, row in subset.iterrows():
        period       = row["period"]
        actual_spend = row["actual_spend"]
        notes        = row["notes"] if pd.notna(row["notes"]) else ""

        # --- null_actual_spend guard (enforcement rules 2–4, 11) ---
        if pd.isna(actual_spend):
            output_rows.append({
                "period":       period,
                "ward":         ward,
                "category":     category,
                "actual_spend": None,
                "growth_value": None,
                "formula":      "NOT COMPUTED — actual_spend is null",
                "null_flag":    True,
                "null_reason":  notes if notes else "(no reason recorded in notes column)",
            })
            continue

        # --- compute growth ---
        growth_value = None
        formula_str  = None

        if growth_type == "MoM":
            # Month-over-month: (current - previous) / previous * 100
            # Find the immediately preceding period row for same ward+category
            prev_rows = subset[subset["period"] < period].sort_values("period")
            if prev_rows.empty:
                growth_value = None
                formula_str  = (
                    f"MoM: (actual_spend[{period}] - actual_spend[prev]) / actual_spend[prev] × 100 "
                    f"— no prior period available; growth not computed"
                )
            else:
                prev_row          = prev_rows.iloc[-1]
                prev_actual_spend = prev_row["actual_spend"]
                prev_period       = prev_row["period"]

                if pd.isna(prev_actual_spend):
                    growth_value = None
                    formula_str  = (
                        f"MoM: (actual_spend[{period}] - actual_spend[{prev_period}]) "
                        f"/ actual_spend[{prev_period}] × 100 "
                        f"— prior period ({prev_period}) has null actual_spend; growth not computed"
                    )
                elif prev_actual_spend == 0:
                    growth_value = None
                    formula_str  = (
                        f"MoM: (actual_spend[{period}] - actual_spend[{prev_period}]) "
                        f"/ actual_spend[{prev_period}] × 100 "
                        f"— prior period ({prev_period}) actual_spend is 0; division undefined"
                    )
                else:
                    growth_value = round(
                        (actual_spend - prev_actual_spend) / prev_actual_spend * 100, 2
                    )
                    formula_str = (
                        f"MoM: ({actual_spend} - {prev_actual_spend}) "
                        f"/ {prev_actual_spend} × 100 "
                        f"= {growth_value}%  [periods: {prev_period} → {period}]"
                    )

        elif growth_type == "YoY":
            # Year-over-year: compare same month, prior year
            # Since data spans only 2024, prior-year rows won't exist — report clearly.
            month        = period.split("-")[1]  # MM
            prior_period = f"{int(period.split('-')[0]) - 1}-{month}"
            prior_rows   = subset[subset["period"] == prior_period]

            if prior_rows.empty:
                growth_value = None
                formula_str  = (
                    f"YoY: (actual_spend[{period}] - actual_spend[{prior_period}]) "
                    f"/ actual_spend[{prior_period}] × 100 "
                    f"— prior year period ({prior_period}) not present in dataset; growth not computed"
                )
            else:
                prior_actual_spend = prior_rows.iloc[0]["actual_spend"]
                if pd.isna(prior_actual_spend):
                    growth_value = None
                    formula_str  = (
                        f"YoY: (actual_spend[{period}] - actual_spend[{prior_period}]) "
                        f"/ actual_spend[{prior_period}] × 100 "
                        f"— prior year period ({prior_period}) has null actual_spend; growth not computed"
                    )
                elif prior_actual_spend == 0:
                    growth_value = None
                    formula_str  = (
                        f"YoY: (actual_spend[{period}] - actual_spend[{prior_period}]) "
                        f"/ actual_spend[{prior_period}] × 100 "
                        f"— prior year period ({prior_period}) actual_spend is 0; division undefined"
                    )
                else:
                    growth_value = round(
                        (actual_spend - prior_actual_spend) / prior_actual_spend * 100, 2
                    )
                    formula_str = (
                        f"YoY: ({actual_spend} - {prior_actual_spend}) "
                        f"/ {prior_actual_spend} × 100 "
                        f"= {growth_value}%  [periods: {prior_period} → {period}]"
                    )

        output_rows.append({
            "period":       period,
            "ward":         ward,
            "category":     category,
            "actual_spend": actual_spend,
            "growth_value": growth_value,
            "formula":      formula_str,
            "null_flag":    False,
            "null_reason":  "",
        })

    result_df = pd.DataFrame(output_rows, columns=[
        "period", "ward", "category", "actual_spend",
        "growth_value", "formula", "null_flag", "null_reason",
    ])

    return result_df


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="UC-0C: Per-ward, per-category budget growth analysis."
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="Growth type: MoM or YoY (required — will not be guessed)")
    parser.add_argument("--output",      required=True,  help="Output CSV file path")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # --- enforcement: growth_type must be explicit (rule 6) ---
    # argparse sets default=None; we check here for clarity and early exit.
    if args.growth_type is None:
        print(
            "\n[REFUSED] --growth-type was not provided.\n"
            "Please explicitly specify 'MoM' (month-over-month) or 'YoY' (year-over-year).\n"
            "This agent will never guess or default the growth formula.\n",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- skill: load_dataset ---
    print("=" * 70)
    print("STEP 1: Loading and validating dataset")
    print("=" * 70)
    try:
        dataset_result = load_dataset(args.input)
    except (FileNotFoundError, ValidationError, EnforcementError) as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    # --- skill: compute_growth ---
    print("=" * 70)
    print("STEP 2: Computing growth")
    print(f"  Ward        : {args.ward}")
    print(f"  Category    : {args.category}")
    print(f"  Growth type : {args.growth_type}")
    print("=" * 70)
    try:
        result_df = compute_growth(
            dataset_result=dataset_result,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
    except (EnforcementError, ValidationError) as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    # --- summary before writing ---
    print("\n[compute_growth] Growth computation complete.")
    total_rows  = len(result_df)
    null_rows   = result_df["null_flag"].sum()
    computed    = total_rows - null_rows
    print(f"  Total periods : {total_rows}")
    print(f"  Growth computed : {computed}")
    print(f"  Null/flagged rows (growth NOT computed) : {null_rows}")
    if null_rows > 0:
        print("  Flagged rows:")
        for _, r in result_df[result_df["null_flag"]].iterrows():
            print(f"    • {r['period']} — reason: {r['null_reason']}")
    print()

    # --- write output ---
    output_path = args.output
    output_dir  = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    result_df.to_csv(output_path, index=False)
    print("=" * 70)
    print(f"Output written to: {output_path}")
    print("=" * 70)
    print()

    # --- print table to stdout for immediate verification ---
    print(result_df.to_string(index=False))
    print()

    return result_df


if __name__ == "__main__":
    main()