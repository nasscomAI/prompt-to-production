"""
UC-0C app.py — Budget Growth Calculator.
Per-ward per-category growth calculation with strict null handling and explicit formula disclosure.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input budget CSV not found: {input_path}")

    rows = []
    null_count = 0
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2): # 1-indexed header line
            period = row["period"].strip()
            ward = row["ward"].strip()
            category = row["category"].strip()
            budgeted = float(row["budgeted_amount"]) if row["budgeted_amount"] else 0.0
            
            raw_spend = row["actual_spend"].strip()
            if raw_spend == "" or raw_spend is None:
                actual_spend = None
                null_count += 1
            else:
                actual_spend = float(raw_spend)

            notes = row.get("notes", "").strip()
            rows.append({
                "line": i,
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual_spend,
                "notes": notes
            })

    return rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes per-period MoM growth for specified ward and category.
    """
    if not growth_type:
        print("ERROR: --growth-type not specified. Must specify 'MoM' or 'YoY'. Refusing calculation.", file=sys.stderr)
        sys.exit(1)

    if ward.lower() == "all" or category.lower() == "all":
        print("ERROR: All-ward or all-category aggregation is strictly prohibited. Refusing calculation.", file=sys.stderr)
        sys.exit(1)

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda x: x["period"])

    output_rows = []
    prev_spend = None

    for r in filtered:
        curr_spend = r["actual_spend"]
        period = r["period"]
        b_amount = r["budgeted_amount"]
        notes = r["notes"]

        if curr_spend is None:
            growth_str = "NULL (Flagged)"
            formula_str = "N/A - Data missing"
            note_str = notes if notes else "Data not submitted"
        elif prev_spend is None:
            growth_str = "N/A"
            formula_str = "Baseline period"
            note_str = notes
        else:
            pct = ((curr_spend - prev_spend) / prev_spend) * 100.0
            sign = "+" if pct > 0 else ""
            growth_str = f"{sign}{pct:.1f}%"
            formula_str = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100"
            note_str = notes

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": b_amount,
            "actual_spend": curr_spend if curr_spend is not None else "NULL",
            "growth_percent": growth_str,
            "formula_used": formula_str,
            "notes": note_str
        })

        prev_spend = curr_spend

    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth calculation type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV file")

    args = parser.parse_args()

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_percent", "formula_used", "notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth output written to {args.output}")

if __name__ == "__main__":
    main()
