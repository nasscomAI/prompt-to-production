"""
UC-0C — Number That Looks Right
App implementation to calculate budget growth with strict null handling and zero unrequested aggregation.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path: str):
    """
    Reads CSV dataset and returns parsed rows.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    rows = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Computes per-period MoM growth for the specified ward and category.
    Strictly refuses all-ward aggregation and missing growth parameters.
    """
    if not growth_type:
        sys.exit("Error: --growth-type must be specified (e.g., MoM). Aggregation refused.")

    if not ward or ward.lower() == "all":
        sys.exit("Error: All-ward aggregation is strictly prohibited. You must specify a single ward.")

    if not category or category.lower() == "all":
        sys.exit("Error: All-category aggregation is strictly prohibited. You must specify a single category.")

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_spend = None

    for r in filtered:
        period = r["period"]
        raw_actual = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        if raw_actual == "":
            actual_val = None
            growth_str = "NULL"
            formula_str = f"Missing data ({notes})" if notes else "Missing data"
        else:
            actual_val = float(raw_actual)
            if prev_spend is None:
                growth_str = "N/A"
                formula_str = "Base period (no previous month)"
            else:
                pct = ((actual_val - prev_spend) / prev_spend) * 100.0
                growth_str = f"{pct:+.1f}%"
                formula_str = f"({actual_val} - {prev_spend}) / {prev_spend} * 100"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": raw_actual if raw_actual != "" else "NULL",
            "growth": growth_str,
            "formula": formula_str,
            "notes": notes
        })

        if actual_val is not None:
            prev_spend = actual_val
        else:
            prev_spend = None

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth calculation type")
    parser.add_argument("--output", required=True, help="Path to output CSV")

    args = parser.parse_args()
    rows = load_dataset(args.input)
    growth_data = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_data)

    print(f"Growth output successfully generated at {args.output}")

if __name__ == "__main__":
    main()
