"""
UC-0C — Number That Looks Right
App implementation for ward budget growth calculation with strict validation.
"""
import argparse
import csv
import sys
from typing import List, Dict

def load_dataset(input_path: str, ward: str, category: str) -> List[Dict]:
    if not ward or ward.lower() in ["all", "all wards", "total"]:
        raise ValueError("Refused: All-ward aggregation is not permitted. Please specify a single ward.")
    if not category or category.lower() in ["all", "all categories", "total"]:
        raise ValueError("Refused: All-category aggregation is not permitted. Please specify a single category.")

    rows = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip():
                rows.append(r)

    if not rows:
        raise ValueError(f"No records found for ward '{ward}' and category '{category}'.")
    return sorted(rows, key=lambda x: x["period"])

def compute_growth(rows: List[Dict], growth_type: str) -> List[Dict]:
    if not growth_type or growth_type.upper() not in ["MOM", "YOY"]:
        raise ValueError("Refused: --growth-type must be specified as 'MoM' or 'YoY'.")

    output = []
    prev_spend = None

    for i, r in enumerate(rows):
        period = r["period"]
        ward = r["ward"]
        cat = r["category"]
        budgeted = r["budgeted_amount"]
        raw_spend = r["actual_spend"].strip()
        notes = r.get("notes", "").strip()

        if not raw_spend:
            growth_str = "NULL"
            formula = "N/A (actual_spend is NULL)"
            current_spend = None
            if not notes:
                notes = "NULL actual_spend value"
        else:
            current_spend = float(raw_spend)

            if i == 0 or prev_spend is None:
                growth_str = "N/A"
                formula = "N/A (first period)"
            else:
                pct = ((current_spend - prev_spend) / prev_spend) * 100
                sign = "+" if pct > 0 else ""
                growth_str = f"{sign}{pct:.1f}%"
                formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"

        output.append({
            "period": period,
            "ward": ward,
            "category": cat,
            "budgeted_amount": budgeted,
            "actual_spend": raw_spend if raw_spend else "NULL",
            "mom_growth": growth_str,
            "formula": formula,
            "notes": notes
        })

        if current_spend is not None:
            prev_spend = current_spend

    return output

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    try:
        rows = load_dataset(args.input, args.ward, args.category)
        results = compute_growth(rows, args.growth_type)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "mom_growth", "formula", "notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()
