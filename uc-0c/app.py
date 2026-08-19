"""
UC-0C app.py — Ward Budget Aggregator & Growth Calculator
RICE → agents.md → skills.md → CRAFT workflow implementation.
"""
import argparse
import csv
import sys

def load_and_filter_data(input_path: str, ward: str, category: str):
    rows = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip():
                rows.append(r)
    # Sort by period
    rows.sort(key=lambda x: x["period"])
    return rows

def compute_growth(rows: list, growth_type: str):
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError(f"Invalid or missing --growth-type: '{growth_type}'. Must be 'MoM' or 'YoY'.")

    output_rows = []
    prev_spend = None

    for i, r in enumerate(rows):
        period = r["period"]
        ward = r["ward"]
        cat = r["category"]
        budgeted = r["budgeted_amount"]
        raw_spend = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        if not raw_spend or raw_spend.upper() == "NULL" or raw_spend == "":
            growth_rate = "NULL"
            formula = "N/A (Null Spend)"
            spend_val = "NULL"
            notes_out = notes if notes else "Data missing / Null spend"
            prev_spend = None
        else:
            spend_float = float(raw_spend)
            spend_val = f"{spend_float:.1f}"
            notes_out = notes

            if i == 0 or prev_spend is None:
                growth_rate = "N/A"
                formula = "Baseline Period"
            else:
                pct_change = ((spend_float - prev_spend) / prev_spend) * 100.0
                sign = "+" if pct_change > 0 else ""
                growth_rate = f"{sign}{pct_change:.1f}%"
                formula = f"(({spend_float:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"

            prev_spend = spend_float

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": cat,
            "budgeted_amount": budgeted,
            "actual_spend": spend_val,
            "growth_type": growth_type,
            "growth_rate": growth_rate,
            "formula_used": formula,
            "notes": notes_out
        })

    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Aggregator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact Ward name")
    parser.add_argument("--category", required=True, help="Exact Category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    # Refuse all-ward or all-category aggregation
    if not args.ward or args.ward.lower() in ["any", "all"]:
        print("Refused: All-ward or all-category aggregation is prohibited without explicit instruction.", file=sys.stderr)
        sys.exit(1)
    if not args.category or args.category.lower() in ["any", "all"]:
        print("Refused: All-ward or all-category aggregation is prohibited without explicit instruction.", file=sys.stderr)
        sys.exit(1)

    filtered_rows = load_and_filter_data(args.input, args.ward, args.category)
    if not filtered_rows:
        print(f"Error: No matching records found for Ward '{args.ward}' and Category '{args.category}'", file=sys.stderr)
        sys.exit(1)

    results = compute_growth(filtered_rows, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_type", "growth_rate", "formula_used", "notes"]
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()
