"""
UC-0C — Budget Growth Analysis Agent
Implements the two skills defined in skills.md:
  · load_dataset  — reads CSV, validates columns, reports null-manifest before returning
  · compute_growth — computes MoM or YoY per ward+category with formula shown in every row

Enforcement rules from agents.md:
  1. Never aggregate across wards or categories — refuse if asked.
  2. Flag every null actual_spend row before computing — report null reason from notes.
  3. Show formula used in every output row alongside the result.
  4. If --growth-type is not specified — refuse and ask; never silently pick one.

Run command (from README):
  python app.py \
    --input ../data/budget/ward_budget.csv \
    --ward "Ward 1 – Kasba" \
    --category "Roads & Pothole Repair" \
    --growth-type MoM \
    --output growth_output.csv
"""

import argparse
import csv
import sys


# ---------------------------------------------------------------------------
# SKILL: load_dataset
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str) -> list[dict]:
    """
    Reads ward_budget.csv, validates all required columns are present,
    then prints a null-manifest of every blank actual_spend row (with its
    null reason from the notes column) before returning the dataset.

    Raises SystemExit if the file cannot be opened or columns are missing.
    Never zero-fills or imputes null values.
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                sys.exit(f"[ERROR] load_dataset: '{file_path}' appears to be empty.")

            missing = REQUIRED_COLUMNS - {c.strip() for c in reader.fieldnames}
            if missing:
                sys.exit(
                    f"[ERROR] load_dataset: Missing required columns: {sorted(missing)}\n"
                    f"        Found: {list(reader.fieldnames)}"
                )

            rows = [row for row in reader]
    except FileNotFoundError:
        sys.exit(f"[ERROR] load_dataset: File not found — '{file_path}'")
    except Exception as exc:
        sys.exit(f"[ERROR] load_dataset: Could not read file — {exc}")

    # --- Null-manifest: report BEFORE any computation (enforcement rule 2) ---
    null_rows = [
        r for r in rows if r["actual_spend"].strip() == ""
    ]
    print(f"\n[load_dataset] Loaded {len(rows)} rows from '{file_path}'.")
    print(f"[load_dataset] NULL actual_spend count: {len(null_rows)}")
    if null_rows:
        print("[load_dataset] NULL manifest (flagged before any computation):")
        for r in null_rows:
            reason = r["notes"].strip() or "no reason recorded"
            print(f"  · {r['period']} · {r['ward']} · {r['category']} → NULL reason: {reason}")
    print()

    return rows


# ---------------------------------------------------------------------------
# SKILL: compute_growth
# ---------------------------------------------------------------------------

FORMULA_MOM = "MoM = (current − previous) / previous × 100"
FORMULA_YOY = "YoY = (current_year − previous_year) / previous_year × 100"


def compute_growth(
    dataset: list[dict],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict]:
    """
    Filters the dataset to the specified ward + category, then computes
    growth rates (MoM or YoY) for each period.

    Returns a list of row dicts with:
      period, actual_spend, growth_rate, formula, null_reason

    Enforcement:
      · growth_type must be 'MoM' or 'YoY' — caller must supply it explicitly.
      · Null rows are emitted as flagged entries; adjacent rows are still computed.
      · budgeted_amount is never used as a proxy for actual_spend.
    """
    growth_type = growth_type.upper()
    if growth_type not in ("MOM", "YOY"):
        sys.exit(
            "[ERROR] compute_growth: --growth-type must be 'MoM' or 'YoY'.\n"
            "        Please specify one explicitly — this agent never guesses."
        )

    # Validate ward and category exist in the dataset
    all_wards = {r["ward"] for r in dataset}
    all_categories = {r["category"] for r in dataset}

    if ward not in all_wards:
        sys.exit(
            f"[ERROR] compute_growth: Ward '{ward}' not found in dataset.\n"
            f"        Available wards: {sorted(all_wards)}"
        )
    if category not in all_categories:
        sys.exit(
            f"[ERROR] compute_growth: Category '{category}' not found in dataset.\n"
            f"        Available categories: {sorted(all_categories)}"
        )

    # Filter to the single ward + category slice (no cross-ward/category aggregation)
    subset = [
        r for r in dataset
        if r["ward"] == ward and r["category"] == category
    ]
    subset.sort(key=lambda r: r["period"])

    formula_label = FORMULA_MOM if growth_type == "MOM" else FORMULA_YOY
    output_rows = []

    for i, row in enumerate(subset):
        period = row["period"]
        raw_spend = row["actual_spend"].strip()
        null_reason = row["notes"].strip() if raw_spend == "" else ""

        # Current value
        if raw_spend == "":
            current_val = None
        else:
            try:
                current_val = float(raw_spend)
            except ValueError:
                current_val = None
                null_reason = f"unparseable value: '{raw_spend}'"

        # Find the comparison period
        prev_val = None
        if growth_type == "MOM":
            if i > 0:
                prev_raw = subset[i - 1]["actual_spend"].strip()
                prev_val = float(prev_raw) if prev_raw != "" else None
        else:  # YOY
            # Find same month in prior year
            try:
                yyyy, mm = period.split("-")
                prior_period = f"{int(yyyy) - 1}-{mm}"
                prior_rows = [r for r in subset if r["period"] == prior_period]
                if prior_rows:
                    prior_raw = prior_rows[0]["actual_spend"].strip()
                    prev_val = float(prior_raw) if prior_raw != "" else None
            except Exception:
                prev_val = None

        # Compute growth rate
        if current_val is None:
            growth_rate = "NULL"
            rate_display = f"NULL ({null_reason})"
        elif prev_val is None:
            growth_rate = "N/A"
            rate_display = "N/A (no prior period or prior period is null)"
        elif prev_val == 0:
            growth_rate = "N/A"
            rate_display = "N/A (prior period spend is zero — division undefined)"
        else:
            rate = (current_val - prev_val) / prev_val * 100
            growth_rate = f"{rate:+.1f}%"
            rate_display = growth_rate

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": raw_spend if raw_spend != "" else "NULL",
            "growth_rate": rate_display,
            "formula": formula_label if growth_rate not in ("NULL", "N/A") else "N/A — see growth_rate",
            "null_reason": null_reason,
        })

    return output_rows


# ---------------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------------

def write_output(rows: list[dict], output_path: str) -> None:
    """Writes the growth table to a CSV file."""
    if not rows:
        print("[WARN] No output rows to write.")
        return

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_rate", "formula", "null_reason"]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[output] Written {len(rows)} rows → '{output_path}'")


def print_table(rows: list[dict]) -> None:
    """Prints a formatted summary table to stdout."""
    header = f"{'Period':<10}  {'Actual Spend':>14}  {'Growth Rate':>14}  {'Formula':<45}  Null Reason"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(
            f"{r['period']:<10}  "
            f"{r['actual_spend']:>14}  "
            f"{r['growth_rate']:>14}  "
            f"{r['formula']:<45}  "
            f"{r['null_reason']}"
        )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Analysis Agent — per-ward, per-category MoM/YoY growth."
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category",    required=True,  help="Exact category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument(
        "--growth-type",
        required=False,
        default=None,
        dest="growth_type",
        help="Growth calculation type: 'MoM' or 'YoY' — REQUIRED, never defaulted.",
    )
    parser.add_argument("--output",      required=False, default="growth_output.csv", help="Output CSV path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Enforcement rule 4 — refuse if --growth-type not supplied
    if args.growth_type is None:
        sys.exit(
            "[REFUSED] --growth-type was not specified.\n"
            "          Please re-run with --growth-type MoM or --growth-type YoY.\n"
            "          This agent never silently picks a growth type."
        )

    # Skill: load_dataset (prints null-manifest before returning)
    dataset = load_dataset(args.input)

    print(f"[agent] Computing {args.growth_type} growth for:")
    print(f"        Ward     : {args.ward}")
    print(f"        Category : {args.category}\n")

    # Skill: compute_growth
    result_rows = compute_growth(
        dataset=dataset,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
    )

    # Print table to stdout
    print_table(result_rows)
    print()

    # Write CSV output
    write_output(result_rows, args.output)


if __name__ == "__main__":
    main()
