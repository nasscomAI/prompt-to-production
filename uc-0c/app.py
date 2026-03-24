"""
UC-0C — Number That Looks Right
Computes MoM (Month-over-Month) or YoY growth for ward budget data.
Handles null rows, refuses cross-ward aggregation, shows formula per row.

Usage:
    python app.py --input ../data/budget/ward_budget.csv \
                  --ward "Ward 1 - Kasba" \
                  --category "Roads & Pothole Repair" \
                  --growth-type MoM \
                  --output growth_output.csv

    python app.py --input ../data/budget/ward_budget.csv   # interactive mode
"""
import argparse
import csv
import sys
from typing import Optional


def load_dataset(file_path: str) -> tuple[list[dict], list[dict]]:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    Returns: (clean_rows, null_rows)
    Enforcement: never silently skip nulls — report them first.
    """
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend"}

    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows   = list(reader)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    if not rows:
        print("[ERROR] Dataset is empty.")
        sys.exit(1)

    missing_cols = required_cols - set(rows[0].keys())
    if missing_cols:
        print(f"[ERROR] Missing columns: {missing_cols}")
        sys.exit(1)

    clean_rows = []
    null_rows  = []

    for row in rows:
        spend = row.get("actual_spend", "").strip()
        if spend == "" or spend is None:
            null_rows.append(row)
        else:
            try:
                row["actual_spend"] = float(spend)
                row["budgeted_amount"] = float(row.get("budgeted_amount", 0))
                clean_rows.append(row)
            except ValueError:
                null_rows.append(row)

    # Report nulls before any computation (enforcement rule 2)
    print(f"[DATASET] Total rows: {len(rows)}  |  Clean: {len(clean_rows)}  |  Null actual_spend: {len(null_rows)}")
    if null_rows:
        print("[NULL ROWS — will NOT be included in growth calculation]:")
        for r in null_rows:
            note = r.get("notes", "no note").strip() or "no note"
            print(f"  {r['period']}  {r['ward']}  {r['category']}  → reason: {note}")
        print()

    return clean_rows, null_rows


def compute_growth(
    rows: list[dict],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict]:
    """
    Compute MoM or YoY growth for a specific ward + category.
    Enforcement:
    - Never aggregate across wards/categories (per agents.md rule 1)
    - Show formula for every output row (rule 3)
    - Refuse if growth_type not MoM or YoY (rule 4)
    """
    growth_type = growth_type.upper()
    if growth_type not in ("MOM", "YOY"):
        print(f"[ERROR] --growth-type must be MoM or YoY. Got: '{growth_type}'")
        print("Please specify exactly which growth type you want. Refusing to guess.")
        sys.exit(1)

    # Filter to exact ward + category (agents.md rule 1: no cross-aggregation)
    filtered = [
        r for r in rows
        if r["ward"].strip().lower() == ward.strip().lower()
        and r["category"].strip().lower() == category.strip().lower()
    ]

    if not filtered:
        print(f"[ERROR] No data found for ward='{ward}' category='{category}'")
        print("Available wards:")
        for w in sorted(set(r["ward"] for r in rows)):
            print(f"  {w}")
        print("Available categories:")
        for c in sorted(set(r["category"] for r in rows)):
            print(f"  {c}")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []

    if growth_type == "MOM":
        for i, row in enumerate(filtered):
            if i == 0:
                results.append({
                    "period":        row["period"],
                    "ward":          row["ward"],
                    "category":      row["category"],
                    "actual_spend":  row["actual_spend"],
                    "growth_pct":    "N/A (first period)",
                    "formula":       "No prior month",
                    "flag":          "",
                })
                continue

            prev  = filtered[i - 1]
            cur   = row["actual_spend"]
            prior = prev["actual_spend"]

            if prior == 0:
                growth = "UNDEFINED (prior=0)"
                formula = f"({cur} - 0) / 0 × 100 — division by zero"
                flag = "NEEDS_REVIEW"
            else:
                growth  = round((cur - prior) / prior * 100, 1)
                formula = f"({cur} - {prior}) / {prior} × 100 = {growth}%"
                flag    = ""

            results.append({
                "period":        row["period"],
                "ward":          row["ward"],
                "category":      row["category"],
                "actual_spend":  cur,
                "growth_pct":    f"{growth}%" if isinstance(growth, float) else growth,
                "formula":       formula,
                "flag":          flag,
            })

    elif growth_type == "YOY":
        # Group by month number across years
        by_month: dict[str, list] = {}
        for row in filtered:
            month_key = row["period"][5:]  # MM part
            by_month.setdefault(month_key, []).append(row)

        for month_key in sorted(by_month):
            month_rows = sorted(by_month[month_key], key=lambda r: r["period"])
            for i, row in enumerate(month_rows):
                if i == 0:
                    results.append({
                        "period":        row["period"],
                        "ward":          row["ward"],
                        "category":      row["category"],
                        "actual_spend":  row["actual_spend"],
                        "growth_pct":    "N/A (first year)",
                        "formula":       "No prior year data",
                        "flag":          "",
                    })
                    continue
                prev  = month_rows[i - 1]
                cur   = row["actual_spend"]
                prior = prev["actual_spend"]
                if prior == 0:
                    growth  = "UNDEFINED (prior=0)"
                    formula = "division by zero"
                    flag    = "NEEDS_REVIEW"
                else:
                    growth  = round((cur - prior) / prior * 100, 1)
                    formula = f"({cur} - {prior}) / {prior} × 100 = {growth}%"
                    flag    = ""
                results.append({
                    "period":        row["period"],
                    "ward":          row["ward"],
                    "category":      row["category"],
                    "actual_spend":  cur,
                    "growth_pct":    f"{growth}%" if isinstance(growth, float) else growth,
                    "formula":       formula,
                    "flag":          flag,
                })

        results.sort(key=lambda r: r["period"])

    return results


def print_results(results: list[dict], growth_type: str):
    print()
    print("═" * 90)
    print(f"GROWTH ANALYSIS ({growth_type})  |  Ward: {results[0]['ward']}  |  Category: {results[0]['category']}")
    print("═" * 90)
    print(f"{'Period':<12} {'Actual Spend (₹L)':<20} {'Growth':<15} {'Formula'}")
    print("-" * 90)
    for r in results:
        flag_marker = " ⚠ NEEDS_REVIEW" if r["flag"] == "NEEDS_REVIEW" else ""
        print(f"{r['period']:<12} {str(r['actual_spend']):<20} {str(r['growth_pct']):<15} {r['formula']}{flag_marker}")
    print("═" * 90)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=False, help="Ward name (exact)")
    parser.add_argument("--category",    required=False, help="Category name (exact)")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output",      required=False, help="Path to write output CSV")
    args = parser.parse_args()

    clean_rows, _ = load_dataset(args.input)

    # Interactive prompts if not provided
    ward = args.ward
    if not ward:
        wards = sorted(set(r["ward"] for r in clean_rows))
        print("Available wards:")
        for i, w in enumerate(wards, 1):
            print(f"  {i}. {w}")
        idx  = int(input("Select ward number: ")) - 1
        ward = wards[idx]

    category = args.category
    if not category:
        cats = sorted(set(r["category"] for r in clean_rows))
        print("Available categories:")
        for i, c in enumerate(cats, 1):
            print(f"  {i}. {c}")
        idx      = int(input("Select category number: ")) - 1
        category = cats[idx]

    growth_type = args.growth_type
    if not growth_type:
        # Enforcement rule 4: refuse to guess — must ask
        print("[REQUIRED] --growth-type not specified.")
        growth_type = input("Enter growth type (MoM / YoY): ").strip()
        if growth_type.upper() not in ("MOM", "YOY"):
            print("[ERROR] Must be MoM or YoY. Exiting.")
            sys.exit(1)

    results = compute_growth(clean_rows, ward, category, growth_type)
    print_results(results, growth_type.upper())

    if args.output:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"]
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"[OK] Written to: {args.output}")


if __name__ == "__main__":
    main()
