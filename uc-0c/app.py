"""
UC-0C app.py — Budget Growth Analysis Agent
============================================
Driven by agents.md (role / intent / context / enforcement) and
skills.md (load_dataset + compute_growth).

Run command (from README.md):
    python app.py \\
        --input ../data/budget/ward_budget.csv \\
        --ward "Ward 1 – Kasba" \\
        --category "Roads & Pothole Repair" \\
        --growth-type MoM \\
        --output growth_output.csv
"""

import argparse
import csv
import sys
from typing import Optional, Sequence


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
VALID_GROWTH_TYPES = {"MoM", "YoY"}


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(file_path: str) -> tuple[list[dict], list[dict]]:
    """
    Skill: load_dataset
    -------------------
    Reads the ward_budget CSV, validates required columns, then produces a
    pre-flight null report before returning the dataset.

    Returns:
        (rows, null_rows)
        rows      — list of all row dicts (actual_spend may be None)
        null_rows — list of dicts describing each null actual_spend row
    """
    # --- File read ---
    try:
        with open(file_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)

            fieldnames: Sequence[str] = reader.fieldnames or []
            if not fieldnames:
                print(f"[ERROR] '{file_path}' appears to be empty or has no header row.", file=sys.stderr)
                sys.exit(1)
            present_columns: set[str] = {col for col in fieldnames}
            missing = REQUIRED_COLUMNS - present_columns
            if missing:
                print(
                    f"[ERROR] Missing required columns: {', '.join(sorted(missing))}",
                    file=sys.stderr,
                )
                sys.exit(1)

            rows = list(reader)

    except FileNotFoundError:
        print(f"[ERROR] File not found: '{file_path}'. Provide a valid path — the agent will not guess.", file=sys.stderr)
        sys.exit(1)

    # --- Normalise actual_spend to float | None ---
    for row in rows:
        raw = row["actual_spend"].strip() if row.get("actual_spend") else ""
        row["actual_spend"] = float(raw) if raw else None

    # --- Pre-flight null report (enforcement rule 2) ---
    null_rows = [r for r in rows if r["actual_spend"] is None]

    print(f"[load_dataset] Total rows loaded : {len(rows)}")
    print(f"[load_dataset] Null actual_spend  : {len(null_rows)}")
    if null_rows:
        print("[load_dataset] Null row details:")
        for nr in null_rows:
            reason = nr.get("notes", "").strip() or "no reason given"
            print(f"  ▸ {nr['period']} · {nr['ward']} · {nr['category']} — reason: {reason}")
    print()

    return rows, null_rows


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------
def compute_growth(
    rows: list[dict],
    ward: Optional[list[str]] = None,
    category: Optional[list[str]] = None,
    growth_type: str = "MoM",
) -> list[dict]:
    """
    Skill: compute_growth
    ---------------------
    Processes the dataset for the requested ward + category (or all if omitted),
    computing per-period growth. Null rows are flagged and excluded from
    computation (enforcement rules 2 & 3).

    growth_type must be 'MoM' or 'YoY' — refuses otherwise (enforcement rule 4).

    Returns:
        List of result dicts with keys:
            Ward, Category, Period, Actual Spend (₹ lakh), MoM Growth, formula_used, null_flag
    """
    # --- Validate growth_type (enforcement rule 4) ---
    if growth_type not in VALID_GROWTH_TYPES:
        print(
            f"[ERROR] --growth-type '{growth_type}' is not recognised. "
            f"Allowed values: {', '.join(sorted(VALID_GROWTH_TYPES))}. "
            "Please specify one explicitly — the agent will not guess.",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Identify targets (all or filtered) ---
    # Normalise filters to sets of stripped strings
    ward_filter = {w.strip() for w in ward} if ward else None
    cat_filter = {c.strip() for c in category} if category else None

    unique_targets: set[tuple[str, str]] = set()
    for r in rows:
        w_val: str = r.get("ward", "").strip()
        c_val: str = r.get("category", "").strip()
        if not w_val or not c_val:
            continue
        
        # Apply filters if present
        if isinstance(ward_filter, set) and w_val not in ward_filter:
            continue
        if isinstance(cat_filter, set) and c_val not in cat_filter:
            continue
            
        unique_targets.add((w_val, c_val))
    
    targets = sorted(list(unique_targets))

    all_results: list[dict] = []

    for target_ward, target_cat in targets:
        # --- Filter to ward + category only (enforcement rule 1) ---
        subset = [
            r for r in rows
            if r["ward"].strip() == target_ward and r["category"].strip() == target_cat
        ]

        if not subset:
            continue

        # Sort chronologically
        subset.sort(key=lambda r: r["period"])

        for i, row in enumerate(subset):
            period = row["period"]
            spend: Optional[float] = row["actual_spend"]
            null_flag = spend is None
            growth_value: Optional[float] = None
            formula_used = "N/A — null actual_spend, not computed"

            if null_flag:
                # Flagged row — no computation (enforcement rules 2 & 3)
                reason = row.get("notes", "").strip() or "no reason given"
                formula_used = f"SKIPPED — actual_spend is null ({reason})"
            else:
                if growth_type == "MoM":
                    # MoM: (current - previous) / previous * 100
                    prev_spend = _find_prev_spend(subset, i)
                    if prev_spend is None:
                        formula_used = "MoM — no prior period available (first row)"
                    else:
                        growth_value = ((spend - prev_spend) / prev_spend) * 100
                        formula_used = (
                            f"MoM = (current - previous) / previous × 100"
                            f" = ({spend} - {prev_spend}) / {prev_spend} × 100"
                        )

                elif growth_type == "YoY":
                    formula_used = (
                        "YoY = (current_year - prior_year) / prior_year × 100 "
                        "— prior-year data not available in this dataset (Jan–Dec 2024 only)"
                    )
                    growth_value = None

            all_results.append(
                {
                    "Ward": target_ward,
                    "Category": target_cat,
                    "Period": period,
                    "Actual Spend (₹ lakh)": "" if spend is None else spend,
                    "MoM Growth": "" if growth_value is None else f"{growth_value:+.1f}%",
                    "Formula": formula_used,
                    "Null Flag": str(null_flag),
                }
            )

    if not all_results:
        print(f"[ERROR] No data found matching the filters.", file=sys.stderr)
        sys.exit(1)

    return all_results


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _find_prev_spend(subset: list[dict], current_index: int) -> Optional[float]:
    """Walk backwards from current_index to find the most recent non-null spend."""
    for j in range(current_index - 1, -1, -1):
        if subset[j]["actual_spend"] is not None:
            return float(subset[j]["actual_spend"])
    return None


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------
def write_output(results: list[dict], output_path: str) -> None:
    """Write the per-ward per-category growth table to a CSV file."""
    fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "MoM Growth", "Formula", "Null Flag"]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"[output] {len(results)} rows written to '{output_path}'")


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Analysis Agent — per-ward per-category only.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            '  python app.py \\\n'
            '    --input ../data/budget/ward_budget.csv \\\n'
            '    --ward "Ward 1 – Kasba" \\\n'
            '    --category "Roads & Pothole Repair" \\\n'
            '    --growth-type MoM \\\n'
            '    --output growth_output.csv'
        ),
    )
    parser.add_argument("--input",       required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=False, nargs="+", help="Ward name(s) (optional — process all if omitted)")
    parser.add_argument("--category",    required=False, nargs="+", help="Category name(s) (optional — process all if omitted)")
    parser.add_argument("--growth-type", required=True, dest="growth_type",
                        help="Growth type: MoM or YoY (required — agent will not guess)")
    parser.add_argument("--output",      required=True, help="Path for output CSV")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Enforcement rule 4: --growth-type is required by argparse; validated inside compute_growth
    print(f"=== UC-0C Budget Growth Analysis Agent ===")
    print(f"Input     : {args.input}")
    print(f"Ward      : {args.ward}")
    print(f"Category  : {args.category}")
    print(f"GrowthType: {args.growth_type}")
    print(f"Output    : {args.output}")
    print()

    # Skill 1: load_dataset
    rows, _ = load_dataset(args.input)

    # Skill 2: compute_growth
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Write output
    write_output(results, args.output)


if __name__ == "__main__":
    main()
