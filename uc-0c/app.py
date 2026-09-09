"""
UC-0C — Budget Growth Calculator
Civic Tech Edition: Enforces granular ward/category analysis, null transparency, and formula visibility.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str):
    """
    Reads CSV, validates columns, and identifies all null actual_spend rows.
    Returns: (list of row dicts, list of null row dicts)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    records = []
    null_rows = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            records.append(row)
            actual = row.get("actual_spend", "").strip()
            if not actual:
                null_rows.append({
                    "row_number": idx,
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": row.get("notes", "")
                })

    return records, null_rows


def compute_growth(records: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes growth for a specific ward and category.
    Refuses all-ward aggregation, requires explicit growth-type, and displays exact formulas.
    """
    if not ward or ward.strip().lower() in ["all", "all wards", "all-ward"]:
        print("REFUSAL ERROR: Aggregation across all wards is prohibited by policy. You must specify a single ward.", file=sys.stderr)
        sys.exit(1)

    if not category or category.strip().lower() in ["all", "all categories"]:
        print("REFUSAL ERROR: Aggregation across all categories is prohibited. You must specify a single category.", file=sys.stderr)
        sys.exit(1)

    if not growth_type or growth_type.strip().upper() not in ["MOM", "YOY"]:
        print("REFUSAL ERROR: Growth type must be explicitly specified (--growth-type MoM or YoY). Silent assumption is prohibited.", file=sys.stderr)
        sys.exit(1)

    normalized_ward = ward.strip()
    normalized_cat = category.strip()
    growth_type_upper = growth_type.strip().upper()

    # Filter records
    filtered = [
        r for r in records
        if r.get("ward", "").strip() == normalized_ward and r.get("category", "").strip() == normalized_cat
    ]

    if not filtered:
        print(f"No records found for ward '{ward}' and category '{category}'.", file=sys.stderr)
        sys.exit(1)

    filtered.sort(key=lambda x: x.get("period", ""))

    output_rows = []
    prev_spend = None

    for i, row in enumerate(filtered):
        period = row.get("period", "")
        budgeted = row.get("budgeted_amount", "")
        actual_str = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()

        curr_spend = float(actual_str) if actual_str else None

        if i == 0:
            growth_rate = "N/A"
            formula = "Baseline period (no prior month for comparison)"
            status = "BASELINE"
        elif curr_spend is None:
            growth_rate = "NULL / NOT_COMPUTABLE"
            reason = notes if notes else "Missing actual spend value"
            formula = f"Flagged null actual_spend: {reason}"
            status = "FLAGGED_NULL"
        elif prev_spend is None:
            growth_rate = "NULL / NOT_COMPUTABLE"
            formula = "Prior period spend was null; comparison unavailable"
            status = "FLAGGED_PRIOR_NULL"
        else:
            pct_change = ((curr_spend - prev_spend) / prev_spend) * 100.0
            growth_rate = f"{pct_change:+.1f}%"
            formula = f"(({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
            status = "COMPUTED"

        output_rows.append({
            "period": period,
            "ward": normalized_ward,
            "category": normalized_cat,
            "budgeted_amount": budgeted,
            "actual_spend": actual_str if actual_str else "NULL",
            "growth_type": growth_type_upper,
            "growth_rate": growth_rate,
            "formula_used": formula,
            "status": status,
            "notes": notes,
        })

        prev_spend = curr_spend

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (required, all-ward refused)")
    parser.add_argument("--category", required=False, help="Category name (required, all-category refused)")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="MoM or YoY (refuses if omitted)")
    parser.add_argument("--output", default="growth_output.csv", help="Output CSV path")
    args = parser.parse_args()

    input_path = args.input
    if not os.path.exists(input_path):
        repo_root_path = os.path.join(os.path.dirname(__file__), "..", "data", "budget", "ward_budget.csv")
        if os.path.exists(repo_root_path):
            input_path = repo_root_path

    records, null_rows = load_dataset(input_path)

    print(f"Loaded {len(records)} records from {input_path}.")
    print(f"Identified {len(null_rows)} deliberate null actual_spend rows:")
    for nr in null_rows:
        print(f"  - Row {nr['row_number']}: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")

    if not args.ward or not args.category or not args.growth_type:
        print("\nNotice: Running without ward/category/growth-type triggers policy refusal enforcement.", file=sys.stderr)
        compute_growth(records, args.ward, args.category, args.growth_type)
        return

    output_rows = compute_growth(records, args.ward, args.category, args.growth_type)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_rate",
        "formula_used",
        "status",
        "notes",
    ]

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nGrowth computation complete. Results written to {args.output}")


if __name__ == "__main__":
    main()
