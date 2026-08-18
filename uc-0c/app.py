"""
UC-0C — Budget Growth Calculator
Usage:
    python app.py \
      --input ../data/budget/ward_budget.csv \
      --ward "Ward 1 – Kasba" \
      --category "Roads & Pothole Repair" \
      --growth-type MoM \
      --output growth_output.csv

Computes per-period spend growth for ONE ward + ONE category.
Never aggregates across wards or categories.
Flags and skips null actual_spend rows.
Shows formula alongside every calculated result.
"""

import argparse
import csv
import sys
import os


# ── Skill: load_dataset ────────────────────────────────────────────────────────

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

def load_dataset(filepath: str):
    """
    Reads the ward_budget CSV, validates columns, reports null rows.
    Returns: (rows: list[dict], null_rows: list[dict])
    """
    if not os.path.isfile(filepath):
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            print(f"ERROR: Missing columns: {missing}", file=sys.stderr)
            sys.exit(1)
        rows = list(reader)

    null_rows = [
        r for r in rows
        if r.get("actual_spend", "").strip() == ""
    ]

    # Always report nulls before returning
    if null_rows:
        print(f"\nNULL REPORT — {len(null_rows)} row(s) with missing actual_spend:")
        for r in null_rows:
            print(f"  ⚑ {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes']}")
        print()

    return rows, null_rows


# ── Skill: compute_growth ─────────────────────────────────────────────────────

def compute_growth(rows, ward: str, category: str, growth_type: str, output_path: str):
    """
    Filters rows to the given ward+category, computes MoM or YoY growth,
    writes output CSV with formula shown in every row.
    """
    if growth_type not in ("MoM", "YoY"):
        print(
            f"ERROR: Growth type '{growth_type}' not recognised.\n"
            "Please provide --growth-type MoM or --growth-type YoY.",
            file=sys.stderr
        )
        sys.exit(1)

    # Validate ward and category exist
    all_wards = {r["ward"] for r in rows}
    all_cats  = {r["category"] for r in rows}

    if ward not in all_wards:
        print(f"ERROR: Ward '{ward}' not found.\nValid wards: {sorted(all_wards)}", file=sys.stderr)
        sys.exit(1)
    if category not in all_cats:
        print(f"ERROR: Category '{category}' not found.\nValid categories: {sorted(all_cats)}", file=sys.stderr)
        sys.exit(1)

    # Filter to the single ward+category
    subset = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]
    subset.sort(key=lambda r: r["period"])

    if growth_type == "MoM":
        formula_template = "MoM = (current - previous) / previous × 100"
    else:
        formula_template = "YoY = (current_year - prior_year) / prior_year × 100"

    out_rows = []
    for i, row in enumerate(subset):
        raw_spend = row.get("actual_spend", "").strip()
        is_null   = raw_spend == ""

        growth_rate = ""
        formula_used = ""
        null_flag   = "NULL — not computed" if is_null else ""

        if not is_null:
            current = float(raw_spend)
            prev_row = None

            if growth_type == "MoM" and i > 0:
                prev_raw = subset[i - 1].get("actual_spend", "").strip()
                if prev_raw:
                    prev_row = float(prev_raw)
            elif growth_type == "YoY":
                # Find row 12 positions back (same month, prior year)
                current_period = row["period"]  # YYYY-MM
                cy, cm = current_period.split("-")
                prior_period = f"{int(cy)-1}-{cm}"
                prior_candidates = [
                    s for s in subset if s["period"] == prior_period
                    and s.get("actual_spend", "").strip() != ""
                ]
                if prior_candidates:
                    prev_row = float(prior_candidates[0]["actual_spend"])

            if prev_row is not None:
                growth_rate = f"{((current - prev_row) / prev_row * 100):+.1f}%"
                formula_used = formula_template
            else:
                formula_used = "N/A — no prior period available"

        out_rows.append({
            "period":       row["period"],
            "ward":         ward,
            "category":     category,
            "actual_spend": raw_spend if not is_null else "NULL",
            "growth_rate":  growth_rate,
            "formula_used": formula_used,
            "null_flag":    null_flag,
        })

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_rate", "formula_used", "null_flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    computed = sum(1 for r in out_rows if r["growth_rate"])
    print(f"Done. {len(out_rows)} rows written → {output_path}  ({computed} growth values computed)")


# ── CLI entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget Growth Calculator (per-ward, per-category only)"
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=True,  dest="growth_type",
                        choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to output CSV")
    args = parser.parse_args()

    rows, _ = load_dataset(args.input)
    compute_growth(rows, args.ward, args.category, args.growth_type, args.output)


if __name__ == "__main__":
    main()
