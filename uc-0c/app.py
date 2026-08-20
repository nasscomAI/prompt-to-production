"""
UC-0C app.py — Ward budget growth analyser (no-API, direct computation)
Implements load_dataset + compute_growth skills from skills.md.
Enforcement from agents.md: per-ward/category only, null rows flagged, formula shown,
growth-type must be explicit, all-ward aggregation refused.
Run: python app.py --input ../data/budget/ward_budget.csv \
       --ward "Ward 1 - Kasba" --category "Roads & Pothole Repair" \
       --growth-type MoM --output growth_output.csv
"""

import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
MOM_FORMULA_TEMPLATE = "((current - previous) / previous) * 100"


# ── Skill: load_dataset ───────────────────────────────────────────────────────

def load_dataset(file_path: str) -> dict:
    """
    Read ward_budget.csv, validate columns, report every null actual_spend row
    with its reason before returning. Never silently skips nulls.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        sys.exit(f"ERROR [load_dataset]: File not found: {path}")
    try:
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = set(reader.fieldnames or [])
    except OSError as e:
        sys.exit(f"ERROR [load_dataset]: Could not read {path}: {e}")

    missing_cols = REQUIRED_COLUMNS - fieldnames
    if missing_cols:
        sys.exit(f"ERROR [load_dataset]: Missing required columns: {sorted(missing_cols)}")

    null_rows = [
        r for r in rows if not (r.get("actual_spend") or "").strip()
    ]

    # Report nulls upfront — enforcement rule: never silently skip.
    print(f"load_dataset: {len(rows)} rows loaded, {len(null_rows)} null actual_spend rows:")
    for nr in null_rows:
        print(f"  NULL  {nr['period']}  {nr['ward']}  {nr['category']}  — {nr.get('notes','').strip()}")
    print()

    return {"rows": rows, "null_rows": null_rows}


# ── Skill: compute_growth ─────────────────────────────────────────────────────

def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Compute per-period MoM growth for one ward + category slice.
    Flags null rows; shows formula on every output row.
    Refuses all-ward/all-category calls and unsupported growth types.
    """
    if not ward or not category:
        sys.exit(
            "REFUSED [compute_growth]: Ward and category must both be specified. "
            "Aggregating across wards or categories is not permitted."
        )

    if growth_type != "MoM":
        sys.exit(
            f"REFUSED [compute_growth]: growth_type '{growth_type}' is not supported. "
            "Please specify --growth-type MoM. No default will be assumed."
        )

    rows = dataset["rows"]
    all_wards = sorted({r["ward"] for r in rows})
    all_categories = sorted({r["category"] for r in rows})

    # Validate ward and category exist.
    if ward not in all_wards:
        sys.exit(
            f"ERROR [compute_growth]: Ward '{ward}' not found in dataset.\n"
            f"Valid wards: {all_wards}"
        )
    if category not in all_categories:
        sys.exit(
            f"ERROR [compute_growth]: Category '{category}' not found in dataset.\n"
            f"Valid categories: {all_categories}"
        )

    # Filter to the requested slice and sort by period.
    slice_rows = [
        r for r in rows if r["ward"] == ward and r["category"] == category
    ]
    slice_rows.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(slice_rows):
        period = row["period"]
        raw_spend = (row.get("actual_spend") or "").strip()
        notes = (row.get("notes") or "").strip()
        is_null = not raw_spend

        current_spend = None if is_null else float(raw_spend)

        # Previous period values.
        prev_row = slice_rows[i - 1] if i > 0 else None
        prev_raw = (prev_row.get("actual_spend") or "").strip() if prev_row else None
        prev_spend = None if (not prev_raw) else float(prev_raw)
        prev_period = prev_row["period"] if prev_row else None

        # Determine flag and compute growth.
        if is_null:
            flag = "NULL_FLAGGED"
            growth_pct = ""
            formula = MOM_FORMULA_TEMPLATE
            note = notes or "null — reason not recorded"
        elif i == 0:
            flag = "NO_PRIOR_PERIOD"
            growth_pct = ""
            formula = MOM_FORMULA_TEMPLATE
            note = "First period — no previous month to compare."
        elif prev_spend is None:
            flag = "NULL_DEPENDENCY"
            growth_pct = ""
            formula = MOM_FORMULA_TEMPLATE
            note = f"Previous period ({prev_period}) is null — growth cannot be computed."
        else:
            growth = ((current_spend - prev_spend) / prev_spend) * 100
            growth_pct = f"{growth:+.1f}%"
            formula = (
                f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                f" = {growth:+.1f}%"
            )
            flag = ""
            note = notes

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": raw_spend if not is_null else "NULL",
            "previous_spend": f"{prev_spend}" if prev_spend is not None else ("NULL" if prev_row else ""),
            "mom_growth": growth_pct,
            "formula": formula,
            "flag": flag,
            "note": note,
        })

    return results


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C: Ward budget MoM growth analyser")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, dest="growth_type",
                        help="Growth formula — must be 'MoM'")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    print(f"load_dataset: loading {args.input} ...", flush=True)
    dataset = load_dataset(args.input)

    print(f"compute_growth: ward='{args.ward}'  category='{args.category}'  type={args.growth_type}", flush=True)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["period", "ward", "category", "actual_spend", "previous_spend",
                  "mom_growth", "formula", "flag", "note"]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nOutput written to {out_path.resolve()}\n")

    # Print summary table to stdout.
    print(f"{'Period':<10}  {'Actual':>8}  {'Previous':>9}  {'MoM Growth':>12}  {'Flag':<18}  Formula")
    print("-" * 100)
    for r in results:
        print(
            f"{r['period']:<10}  {r['actual_spend']:>8}  {r['previous_spend']:>9}  "
            f"{r['mom_growth']:>12}  {r['flag']:<18}  {r['formula']}"
        )


if __name__ == "__main__":
    main()
