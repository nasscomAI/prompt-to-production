"""
UC-0C: Per-ward, per-category budget growth analysis agent.
Computes MoM or YoY growth from ward_budget.csv with null flagging and formula display.

Enforcement rules implemented here:
  1. Never aggregate across wards or categories — refuse if asked.
  2. Flag every null actual_spend row before computing — report reason from notes.
  3. Show full formula in every output row alongside the result.
  4. Refuse if --growth-type is not specified — never default silently.
"""
import argparse
import csv
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("[ERROR] pandas is required: pip install pandas", file=sys.stderr)
    sys.exit(1)

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ---------------------------------------------------------------------------
# Skill 1: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str) -> "pd.DataFrame":
    """Read CSV, validate columns, print null report, return DataFrame."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(path)
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    if df.empty:
        raise ValueError("Dataset is empty.")

    null_rows = df[df["actual_spend"].isna()]
    print(f"[load_dataset] Loaded {len(df)} rows from {path.name}")
    print(f"[load_dataset] Null actual_spend count: {len(null_rows)}")

    if not null_rows.empty:
        print("[load_dataset] Null rows flagged (growth will NOT be computed for these):")
        for _, row in null_rows.iterrows():
            reason = row["notes"] if pd.notna(row["notes"]) else "(no reason given)"
            print(f"  NULL | {row['period']} | {row['ward']} | {row['category']} | Reason: {reason}")

    return df


# ---------------------------------------------------------------------------
# Skill 2: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(
    df: "pd.DataFrame",
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict]:
    """Filter to ward+category and compute per-period growth with formula shown."""
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'."
        )

    available_wards = df["ward"].unique().tolist()
    if ward not in available_wards:
        raise ValueError(
            f"Ward '{ward}' not found in dataset.\nAvailable wards: {available_wards}"
        )

    available_categories = df["category"].unique().tolist()
    if category not in available_categories:
        raise ValueError(
            f"Category '{category}' not found in dataset.\nAvailable categories: {available_categories}"
        )

    subset = (
        df[(df["ward"] == ward) & (df["category"] == category)]
        .sort_values("period")
        .reset_index(drop=True)
    )

    if subset.empty:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'.")

    step = 1 if growth_type == "MoM" else 12
    rows = []

    for idx, (_, row) in enumerate(subset.iterrows()):
        period = row["period"]
        actual = row["actual_spend"]
        notes_val = str(row["notes"]).strip() if pd.notna(row["notes"]) else ""
        is_null = pd.isna(actual)

        if is_null:
            rows.append({
                "period": period,
                "actual_spend": "NULL",
                "prior_spend": "",
                "formula": "NULL_FLAGGED",
                "growth_pct": "",
                "is_null": True,
                "null_reason": notes_val,
            })
            continue

        prior_idx = idx - step
        if prior_idx < 0:
            rows.append({
                "period": period,
                "actual_spend": round(float(actual), 1),
                "prior_spend": "N/A",
                "formula": "NO_PRIOR_PERIOD",
                "growth_pct": "",
                "is_null": False,
                "null_reason": "",
            })
            continue

        prior_row = subset.iloc[prior_idx]
        if pd.isna(prior_row["actual_spend"]):
            rows.append({
                "period": period,
                "actual_spend": round(float(actual), 1),
                "prior_spend": "NULL",
                "formula": "PRIOR_NULL_FLAGGED",
                "growth_pct": "",
                "is_null": False,
                "null_reason": "",
            })
            continue

        current_val = float(actual)
        prior_val = float(prior_row["actual_spend"])
        growth = (current_val - prior_val) / prior_val * 100
        formula = f"({current_val} - {prior_val}) / {prior_val} × 100 = {growth:+.1f}%"

        rows.append({
            "period": period,
            "actual_spend": round(current_val, 1),
            "prior_spend": round(prior_val, 1),
            "formula": formula,
            "growth_pct": f"{growth:+.1f}%",
            "is_null": False,
            "null_reason": "",
        })

    return rows


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Per-ward per-category budget growth analysis"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact string from dataset)")
    parser.add_argument("--category", required=True, help="Category name (exact string from dataset)")
    parser.add_argument(
        "--growth-type",
        required=False,
        default=None,
        help="Growth type: MoM or YoY (required — will not be defaulted)",
    )
    parser.add_argument("--output", required=True, help="Output CSV file path")
    args = parser.parse_args()

    # Enforcement rule 4: refuse if --growth-type is not specified
    if args.growth_type is None:
        print(
            "[ERROR] growth-type is required. "
            "Please specify --growth-type MoM or --growth-type YoY.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        df = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"\n[compute_growth] Ward     : {args.ward}")
    print(f"[compute_growth] Category : {args.category}")
    print(f"[compute_growth] Type     : {args.growth_type}\n")

    try:
        results = compute_growth(df, args.ward, args.category, args.growth_type)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    fieldnames = ["period", "actual_spend", "prior_spend", "formula", "growth_pct", "is_null", "null_reason"]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    null_count = sum(1 for r in results if r["is_null"])
    computed_count = sum(1 for r in results if r["growth_pct"])
    print(f"[done] {len(results)} periods processed — {computed_count} growth values computed, {null_count} null(s) flagged.")
    print(f"[done] Output written to: {output_path}")

    if null_count:
        print(f"\n[WARNING] {null_count} period(s) had null actual_spend — growth was NOT computed for those rows.")


if __name__ == "__main__":
    main()
